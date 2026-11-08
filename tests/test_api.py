from datetime import date, timedelta
import base64
import hashlib
from unittest.mock import patch
import pytest
from jose import jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.config import settings
from app.main import app
from app.models import Activity, Competency, DevelopmentPlan, Goal, PlanCompetency
from app.utils.security import create_access_token, verify_password

START = (date.today()-timedelta(days=30)).isoformat()
END = (date.today()+timedelta(days=60)).isoformat()
DUE = (date.today()+timedelta(days=20)).isoformat()


def plan(client, people, headers, owner='employee'):
    r=client.post('/development-plans/', headers=headers[owner],
                  json={'employee_id':people[owner].id, 'start_date':START, 'end_date':END})
    assert r.status_code==201, r.text
    return r.json()['id']


def content(client, people, headers, db, owner='employee'):
    p=plan(client,people,headers,owner)
    base=f'/development-plans/{p}'
    g=client.post(base+'/goals',headers=headers[owner],json={'description':'Goal','deadline':END})
    assert g.status_code==201,g.text
    gid=g.json()['id']
    a=client.post(f'{base}/goals/{gid}/activities', headers=headers[owner],
                  json={'type':'practice','description':'Practice','deadline':DUE})
    assert a.status_code==201,a.text
    comp=Competency(name='Competency')
    db.add(comp); db.commit()
    r=client.post(base+'/competencies',headers=headers[owner],
                   json={'competency_id':comp.id,'current_level':2,'target_level':4})
    assert r.status_code==201,r.text
    return p,gid,a.json()['id'],comp.id


@pytest.mark.parametrize('path',['/development-plans/','/departments/','/competencies/','/auth/me'])
def test_anonymous(client,path):
    assert client.get(path).status_code==401


def test_login_round_trip(client,people):
    r=client.post('/auth/login',data={'username':' EMPLOYEE@EXAMPLE.COM ','password':'password123'})
    assert r.status_code==200
    token=r.json()['access_token']
    assert isinstance(jwt.get_unverified_claims(token)['sub'],str)
    me=client.get('/auth/me',headers={'Authorization':'Bearer '+token})
    assert me.status_code==200
    assert me.json()['id']==people['employee'].id
    assert 'password_hash' not in me.json()
    assert client.get('/development-plans/',headers={'Authorization':'Bearer '+token}).status_code==200


@pytest.mark.parametrize('login,password,status',[
    ('employee@example.com','wrong',401),('missing@example.com','password123',401),
    ('inactive@example.com','password123',403)])
def test_login_rejections(client,people,login,password,status):
    assert client.post('/auth/login',data={'username':login,'password':password}).status_code==status


@pytest.mark.parametrize('subject',[None,'abc','-1','0','2147483648','1.0',[],123])
def test_invalid_token_subject(client,people,subject):
    token=jwt.encode({'sub':subject,'exp':date.today().toordinal()*86400},
                     settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    assert client.get('/auth/me',headers={'Authorization':'Bearer '+token}).status_code==401


def test_expired_tampered_and_missing_exp(client,people):
    tokens=[create_access_token({'sub':people['employee'].id},timedelta(seconds=-1)),
            'not.a.token',
            jwt.encode({'sub':str(people['employee'].id)},settings.SECRET_KEY,algorithm=settings.ALGORITHM),
            jwt.encode({'sub':str(people['employee'].id),'exp':9999999999},'wrong',algorithm=settings.ALGORITHM)]
    for token in tokens:
        assert client.get('/auth/me',headers={'Authorization':'Bearer '+token}).status_code==401


def test_deactivate_existing_token(client,people,headers,db):
    people['employee'].is_active=False; db.commit()
    assert client.get('/auth/me',headers=headers['employee']).status_code==403


def test_pbkdf2_compatibility():
    salt=b'0123456789abcdef'
    digest=hashlib.pbkdf2_hmac('sha256',b'IprDemo2026!',salt,600000)
    hashed='pbkdf2_sha256$600000$'+base64.b64encode(salt).decode()+'$'+base64.b64encode(digest).decode()
    assert verify_password('IprDemo2026!',hashed)
    assert not verify_password('wrong',hashed)
    assert not verify_password('wrong','invalid hash')


@pytest.mark.parametrize('role',['employee','manager','hr'])
def test_each_role_owns_plan(client,people,headers,role):
    p=plan(client,people,headers,role)
    assert client.get(f'/development-plans/{p}',headers=headers[role]).status_code==200
    assert client.delete(f'/development-plans/{p}',headers=headers[role]).status_code==204


def test_visibility_and_mutation(client,people,headers):
    p=plan(client,people,headers); base=f'/development-plans/{p}'
    assert client.get(base,headers=headers['manager']).status_code==200
    for who in ['other','other_manager','hr']:
        assert client.get(base,headers=headers[who]).status_code==403
        assert not client.get('/development-plans/',headers=headers[who]).json()
    assert client.patch(base,headers=headers['manager'],json={'end_date':END}).status_code==403
    assert client.delete(base,headers=headers['manager']).status_code==403
    assert client.patch(base+'/submit',headers=headers['manager']).status_code==403
    assert client.post(base+'/goals',headers=headers['manager'],json={'description':'X','deadline':END}).status_code==403
    assert client.post('/development-plans/',headers=headers['manager'],
                       json={'employee_id':people['employee'].id,'start_date':START,'end_date':END}).status_code==403


@pytest.mark.parametrize('body',[{'status':'approved'},{'manager_comment':'fake'},{'start_date':None},
                                  {'end_date':None},{'employee_id':1}])
def test_cannot_bypass_workflow_or_null_dates(client,people,headers,body):
    p=plan(client,people,headers)
    assert client.patch(f'/development-plans/{p}',headers=headers['employee'],json=body).status_code==422
    assert client.get(f'/development-plans/{p}',headers=headers['employee']).json()['status']=='draft'


def test_dates_rechecked_and_invalid_changes_rolled_back(client,people,headers,db):
    p,g,a,c=content(client,people,headers,db)
    base=f'/development-plans/{p}'
    before=client.get(base,headers=headers['employee']).json()
    bad=client.patch(base,headers=headers['employee'],json={'end_date':START})
    assert bad.status_code==400
    # В тестовой общей Session явно откатываем незакоммиченные ORM-изменения,
    # как это делает закрытие отдельной Session каждого реального запроса.
    db.rollback()
    assert client.get(base,headers=headers['employee']).json()['end_date']==before['end_date']
    r=client.patch(f'{base}/goals/{g}',headers=headers['employee'],json={'deadline':START})
    assert r.status_code==400
    db.rollback()
    assert client.get(f'{base}/goals/{g}',headers=headers['employee']).json()['deadline']==END


@pytest.mark.parametrize('body',[
    {'description':' ','deadline':END},{'description':None,'deadline':END},
    {'description':'X','deadline':None},{'description':'X','deadline':'bad'}])
def test_goal_validation(client,people,headers,body):
    p=plan(client,people,headers)
    assert client.post(f'/development-plans/{p}/goals',headers=headers['employee'],json=body).status_code==422


def test_full_goal_activity_crud(client,people,headers,db):
    p,g,a,c=content(client,people,headers,db)
    base=f'/development-plans/{p}'; gb=f'{base}/goals/{g}'; ab=f'{gb}/activities/{a}'
    for url in [base+'/goals',gb,gb+'/activities',ab]:
        assert client.get(url,headers=headers['employee']).status_code==200
    assert client.put(gb,headers=headers['employee'],json={'description':'Changed','deadline':END}).status_code==200
    assert client.patch(gb,headers=headers['employee'],json={'description':'Patched'}).json()['id']==g
    assert client.put(ab,headers=headers['employee'],json={'description':'Read','deadline':DUE,'type':'reading'}).status_code==200
    assert client.patch(ab,headers=headers['employee'],json={'description':'Read chapter'}).json()['id']==a
    assert client.put(gb,headers=headers['employee'],json={'description':'Missing date'}).status_code==422
    assert client.put(ab,headers=headers['employee'],json={'description':'Missing fields'}).status_code==422
    assert client.delete(ab,headers=headers['employee']).status_code==204
    assert client.get(ab,headers=headers['employee']).status_code==404
    assert client.delete(gb,headers=headers['employee']).status_code==204
    assert client.get(gb,headers=headers['employee']).status_code==404


@pytest.mark.parametrize('body',[
    {'type':'exam','description':'X','deadline':DUE},
    {'type':'course','description':' ','deadline':DUE},
    {'type':'course','description':'X','deadline':None},
    {'type':None,'description':'X','deadline':DUE}])
def test_activity_validation(client,people,headers,db,body):
    p,g,a,c=content(client,people,headers,db)
    assert client.post(f'/development-plans/{p}/goals/{g}/activities',
                       headers=headers['employee'],json=body).status_code==422


def test_nested_ids_cannot_escape_parent(client,people,headers,db):
    p,g,a,c=content(client,people,headers,db)
    second=plan(client,people,headers)
    for url in [f'/development-plans/{second}/goals/{g}',
                f'/development-plans/{second}/goals/{g}/activities/{a}']:
        assert client.get(url,headers=headers['employee']).status_code==404


def test_cascade(client,people,headers,db):
    p,g,a,c=content(client,people,headers,db)
    r=client.delete(f'/development-plans/{p}',headers=headers['employee'])
    assert r.status_code==204 and r.content==b''
    for model,identity in [(DevelopmentPlan,p),(Goal,g),(Activity,a),(PlanCompetency,(p,c))]:
        assert db.get(model,identity) is None


def test_competency_crud_and_hr_only(client,people,headers):
    body={'name':'New competency','description':'Description'}
    assert client.post('/competencies/',headers=headers['employee'],json=body).status_code==403
    r=client.post('/competencies/',headers=headers['hr'],json=body)
    assert r.status_code==201
    c=r.json()['id']; path=f'/competencies/{c}'
    assert client.get(path,headers=headers['employee']).json()['id']==c
    assert client.post('/competencies/',headers=headers['hr'],json=body).status_code==400
    assert client.put(path,headers=headers['hr'],json={'name':'Replacement'}).json()['description'] is None
    assert client.put(path,headers=headers['hr'],json={'description':'Missing name'}).status_code==422
    assert client.patch(path,headers=headers['hr'],json={'description':None}).status_code==200
    assert client.patch(path,headers=headers['hr'],json={'name':None}).status_code==422
    assert client.delete(path,headers=headers['manager']).status_code==403
    r=client.delete(path,headers=headers['hr']); assert r.status_code==204 and r.content==b''
    assert client.get(path,headers=headers['employee']).status_code==404


def test_plan_levels_and_used_competency(client,people,headers,db):
    p,g,a,c=content(client,people,headers,db); base=f'/development-plans/{p}/competencies'
    assert client.post(base,headers=headers['employee'],json={'competency_id':c,'current_level':2,'target_level':4}).status_code==400
    assert client.patch(base+f'/{c}',headers=headers['employee'],json={'current_level':5}).status_code==400
    db.rollback()
    assert client.patch(base+f'/{c}',headers=headers['employee'],json={'current_level':3,'target_level':5}).status_code==200
    assert client.delete(f'/competencies/{c}',headers=headers['hr']).status_code==400
    assert client.delete(base+f'/{c}',headers=headers['employee']).status_code==204
    assert client.delete(f'/competencies/{c}',headers=headers['hr']).status_code==204


@pytest.mark.parametrize('current,target',[(0,4),(1,6),(4,2),(None,4)])
def test_level_validation(client,people,headers,current,target):
    p=plan(client,people,headers)
    assert client.post(f'/development-plans/{p}/competencies',headers=headers['employee'],
                       json={'competency_id':1,'current_level':current,'target_level':target}).status_code==422


def test_lifecycle_reject_return_approve_complete(client,people,headers,db):
    p,g,a,c=content(client,people,headers,db); base=f'/development-plans/{p}'
    assert client.patch(base+'/submit',headers=headers['employee']).json()['status']=='pending'
    assert client.get('/development-plans/pending-count',headers=headers['manager']).json()['count']==1
    assert client.get('/development-plans/?status_filter=pending',headers=headers['manager']).json()[0]['id']==p
    assert client.patch(base+'/approve',headers=headers['employee'],json={}).status_code==403
    assert client.patch(base+'/reject',headers=headers['manager'],json={'manager_comment':' '}).status_code==422
    assert client.patch(base+'/reject',headers=headers['manager'],json={'manager_comment':'Revise'}).json()['status']=='rejected'
    r=client.patch(base+'/return',headers=headers['employee']); assert r.json()['manager_comment']=='Revise'
    assert client.patch(base+'/submit',headers=headers['employee']).json()['status']=='pending'
    assert client.patch(base+'/approve',headers=headers['manager'],json={}).json()['status']=='approved'
    assert client.patch(base+'/complete-activity',headers=headers['manager'],json={'activity_id':a}).status_code==403
    assert client.patch(base+'/complete-activity',headers=headers['employee'],
                         json={'activity_id':a,'completion_date':(date.today()+timedelta(days=1)).isoformat()}).status_code==400
    assert client.patch(base+'/complete-activity',headers=headers['employee'],
                         json={'activity_id':a,'completion_date':(date.today()-timedelta(days=40)).isoformat()}).status_code==400
    r=client.patch(base+'/complete-activity',headers=headers['employee'],
                   json={'activity_id':a,'completion_date':date.today().isoformat()})
    assert r.status_code==200,r.text
    assert r.json()['status']=='completed' and r.json()['progress']==100
    assert r.json()['goals'][0]['is_completed'] is True
    assert client.delete(base,headers=headers['employee']).status_code==400
    assert client.patch(base,headers=headers['employee'],json={'end_date':END}).status_code==400


def test_late_completion_allowed(client,people,headers,db):
    p,g,a,c=content(client,people,headers,db); base=f'/development-plans/{p}'
    assert client.patch(f'{base}/goals/{g}/activities/{a}',headers=headers['employee'],
                        json={'deadline':(date.today()-timedelta(days=1)).isoformat()}).status_code==200
    client.patch(base+'/submit',headers=headers['employee'])
    client.patch(base+'/approve',headers=headers['manager'],json={})
    assert client.patch(base+'/complete-activity',headers=headers['employee'],
                         json={'activity_id':a,'completion_date':date.today().isoformat()}).json()['status']=='completed'


def test_completion_one_transaction(client,people,headers,db):
    p,g,a,c=content(client,people,headers,db); base=f'/development-plans/{p}'
    client.patch(base+'/submit',headers=headers['employee'])
    client.patch(base+'/approve',headers=headers['manager'],json={})
    with patch.object(db,'commit',side_effect=RuntimeError('simulated failure')):
        with pytest.raises(RuntimeError):
            client.patch(base+'/complete-activity',headers=headers['employee'],json={'activity_id':a})
    db.rollback()
    assert db.get(Activity,a).status=='planned'
    assert db.get(DevelopmentPlan,p).status=='approved'


@pytest.mark.parametrize('state',['pending','approved','rejected','completed'])
def test_non_draft_content_frozen(client,people,headers,db,state):
    p,g,a,c=content(client,people,headers,db)
    row=db.get(DevelopmentPlan,p); row.status=state
    if state=='rejected': row.manager_comment='Revise'
    db.commit()
    base=f'/development-plans/{p}'
    operations=[('patch',base,{'end_date':END}),('delete',base,None),
        ('patch',f'{base}/goals/{g}',{'description':'X'}),
        ('delete',f'{base}/goals/{g}',None),
        ('patch',f'{base}/goals/{g}/activities/{a}',{'description':'X'}),
        ('delete',f'{base}/goals/{g}/activities/{a}',None),
        ('delete',f'{base}/competencies/{c}',None)]
    for method,path,body in operations:
        assert client.request(method,path,headers=headers['employee'],json=body).status_code==400


def test_submit_completeness_and_manager(client,people,headers,db):
    p=plan(client,people,headers); base=f'/development-plans/{p}'
    assert client.patch(base+'/submit',headers=headers['employee']).status_code==400
    people['employee'].manager_id=None; db.commit()
    assert client.patch(base+'/submit',headers=headers['employee']).status_code==400


def test_manager_change_and_inactive_subordinates(client,people,headers,db):
    p,g,a,c=content(client,people,headers,db); base=f'/development-plans/{p}'
    client.patch(base+'/submit',headers=headers['employee'])
    people['employee'].manager_id=people['other_manager'].id; db.commit()
    assert client.patch(base+'/approve',headers=headers['manager'],json={}).status_code==403
    assert client.patch(base+'/approve',headers=headers['other_manager'],json={}).status_code==200
    people['employee'].is_active=False; db.commit()
    assert client.get(base,headers=headers['other_manager']).status_code==403
    assert not client.get('/development-plans/',headers=headers['other_manager']).json()


@pytest.mark.parametrize('url',['/development-plans/?skip=-1','/development-plans/?limit=0',
    '/development-plans/?limit=101','/competencies/?skip=-1','/departments/?limit=0',
    '/development-plans/?status_filter=unknown'])
def test_pagination_validation(client,people,headers,url):
    assert client.get(url,headers=headers['employee']).status_code==422


def test_not_found(client,people,headers):
    for path in ['/development-plans/9999999','/competencies/9999999','/departments/9999999']:
        assert client.get(path,headers=headers['employee']).status_code==404


def test_database_constraints(db,people):
    invalid=DevelopmentPlan(employee_id=people['employee'].id,status='bad',
                            start_date=date.today(),end_date=date.today())
    db.add(invalid)
    with pytest.raises(IntegrityError): db.commit()
    db.rollback()


def test_openapi_security_and_routes(client):
    schema=client.get('/openapi.json').json()
    assert schema['components']['securitySchemes']['OAuth2PasswordBearer']['flows']['password']['tokenUrl']=='auth/login'
    for path,operations in schema['paths'].items():
        for method,op in operations.items():
            if path not in ['/','/health','/auth/login']:
                assert op.get('security'),(path,method)
    for base in ['/competencies','/development-plans']:
        assert {'get','post'}<=schema['paths'][base+'/'].keys()
        assert {'get','put','patch','delete'}<=schema['paths'][base+'/{'+('competency_id' if base=='/competencies' else 'plan_id')+'}'].keys()
    assert client.get('/docs').status_code==200
    assert client.get('/redoc').status_code==200
