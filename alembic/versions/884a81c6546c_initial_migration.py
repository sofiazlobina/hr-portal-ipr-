"""Initial migration: seven tables, constraints and indexes. Frozen schema snapshot."""
from alembic import op

revision = "884a81c6546c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("\nCREATE TABLE competency (\n\tid SERIAL NOT NULL, \n\tname VARCHAR(100) NOT NULL, \n\tdescription TEXT, \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_competency_name CHECK ((btrim(name) <> '')), \n\tUNIQUE (name)\n)\n\n")
    op.execute('CREATE INDEX ix_competency_id ON competency (id)')
    op.execute("\nCREATE TABLE department (\n\tid SERIAL NOT NULL, \n\tname VARCHAR(100) NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_department_name CHECK ((btrim(name) <> '')), \n\tUNIQUE (name)\n)\n\n")
    op.execute('CREATE INDEX ix_department_id ON department (id)')
    op.execute("\nCREATE TABLE app_user (\n\tid SERIAL NOT NULL, \n\tfull_name VARCHAR(150) NOT NULL, \n\temail VARCHAR(254) NOT NULL, \n\tpassword_hash VARCHAR(255) NOT NULL, \n\trole VARCHAR(20) NOT NULL, \n\tdepartment_id INTEGER NOT NULL, \n\tmanager_id INTEGER, \n\tis_active BOOLEAN NOT NULL, \n\tdeactivated_at TIMESTAMP WITH TIME ZONE, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_app_user_full_name CHECK ((btrim(full_name) <> '')), \n\tCONSTRAINT ck_app_user_email CHECK ((email = lower(btrim(email)) AND email <> '')), \n\tCONSTRAINT ck_app_user_password_hash CHECK ((btrim(password_hash) <> '')), \n\tCONSTRAINT ck_app_user_role CHECK ((role IN ('employee', 'manager', 'hr'))), \n\tCONSTRAINT ck_app_user_manager CHECK ((manager_id IS NULL OR manager_id <> id)), \n\tFOREIGN KEY(department_id) REFERENCES department (id), \n\tFOREIGN KEY(manager_id) REFERENCES app_user (id) ON DELETE SET NULL\n)\n\n")
    op.execute('CREATE INDEX idx_app_user_active ON app_user (is_active)')
    op.execute('CREATE INDEX idx_app_user_department ON app_user (department_id)')
    op.execute('CREATE INDEX idx_app_user_manager ON app_user (manager_id)')
    op.execute('CREATE UNIQUE INDEX ix_app_user_email ON app_user (email)')
    op.execute('CREATE INDEX ix_app_user_id ON app_user (id)')
    op.execute("\nCREATE TABLE development_plan (\n\tid SERIAL NOT NULL, \n\temployee_id INTEGER NOT NULL, \n\tstatus VARCHAR(20) NOT NULL, \n\tstart_date DATE NOT NULL, \n\tend_date DATE NOT NULL, \n\tmanager_comment TEXT, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_development_plan_status CHECK ((status IN ('draft', 'pending', 'approved', 'rejected', 'completed'))), \n\tCONSTRAINT ck_development_plan_dates CHECK ((end_date >= start_date)), \n\tCONSTRAINT ck_development_plan_rejection CHECK ((status <> 'rejected' OR (manager_comment IS NOT NULL AND btrim(manager_comment) <> ''))), \n\tFOREIGN KEY(employee_id) REFERENCES app_user (id)\n)\n\n")
    op.execute('CREATE INDEX idx_development_plan_employee ON development_plan (employee_id)')
    op.execute('CREATE INDEX idx_development_plan_status ON development_plan (status)')
    op.execute('CREATE INDEX ix_development_plan_id ON development_plan (id)')
    op.execute("\nCREATE TABLE goal (\n\tid SERIAL NOT NULL, \n\tplan_id INTEGER NOT NULL, \n\tdescription TEXT NOT NULL, \n\tdeadline DATE NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_goal_description CHECK ((btrim(description) <> '')), \n\tFOREIGN KEY(plan_id) REFERENCES development_plan (id) ON DELETE CASCADE\n)\n\n")
    op.execute('CREATE INDEX idx_goal_plan ON goal (plan_id)')
    op.execute('CREATE INDEX ix_goal_id ON goal (id)')
    op.execute('\nCREATE TABLE plan_competency (\n\tplan_id INTEGER NOT NULL, \n\tcompetency_id INTEGER NOT NULL, \n\tcurrent_level INTEGER NOT NULL, \n\ttarget_level INTEGER NOT NULL, \n\tPRIMARY KEY (plan_id, competency_id), \n\tCONSTRAINT ck_plan_competency_current CHECK ((current_level BETWEEN 1 AND 5)), \n\tCONSTRAINT ck_plan_competency_target CHECK ((target_level BETWEEN 1 AND 5)), \n\tCONSTRAINT ck_plan_competency_growth CHECK ((target_level >= current_level)), \n\tFOREIGN KEY(plan_id) REFERENCES development_plan (id) ON DELETE CASCADE, \n\tFOREIGN KEY(competency_id) REFERENCES competency (id)\n)\n\n')
    op.execute('CREATE INDEX idx_plan_competency_competency ON plan_competency (competency_id)')
    op.execute("\nCREATE TABLE activity (\n\tid SERIAL NOT NULL, \n\tgoal_id INTEGER NOT NULL, \n\ttype VARCHAR(20) NOT NULL, \n\tdescription TEXT NOT NULL, \n\tdeadline DATE NOT NULL, \n\tstatus VARCHAR(20) NOT NULL, \n\tcompletion_date DATE, \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_activity_type CHECK ((type IN ('course', 'practice', 'reading'))), \n\tCONSTRAINT ck_activity_description CHECK ((btrim(description) <> '')), \n\tCONSTRAINT ck_activity_status CHECK ((status IN ('planned', 'completed'))), \n\tCONSTRAINT ck_activity_completion CHECK (((status = 'completed' AND completion_date IS NOT NULL) OR (status = 'planned' AND completion_date IS NULL))), \n\tFOREIGN KEY(goal_id) REFERENCES goal (id) ON DELETE CASCADE\n)\n\n")
    op.execute('CREATE INDEX idx_activity_goal ON activity (goal_id)')
    op.execute('CREATE INDEX ix_activity_id ON activity (id)')


def downgrade():
    op.drop_table('activity')
    op.drop_table('plan_competency')
    op.drop_table('goal')
    op.drop_table('development_plan')
    op.drop_table('app_user')
    op.drop_table('department')
    op.drop_table('competency')
