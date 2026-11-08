-- Проверочные запросы после выполнения HR-portal_IPR.sql.
-- Запросы только читают данные.

-- 1. Количество записей: 10, 15, 10, 10, 12, 20 и 15 соответственно.
SELECT 'department' AS table_name, COUNT(*) AS row_count FROM department
UNION ALL SELECT 'app_user', COUNT(*) FROM app_user
UNION ALL SELECT 'competency', COUNT(*) FROM competency
UNION ALL SELECT 'development_plan', COUNT(*) FROM development_plan
UNION ALL SELECT 'goal', COUNT(*) FROM goal
UNION ALL SELECT 'activity', COUNT(*) FROM activity
UNION ALL SELECT 'plan_competency', COUNT(*) FROM plan_competency;

-- 2. Прогресс: число выполненных мероприятий / число всех мероприятий * 100.
-- LEFT JOIN сохраняет пустые планы; COUNT(a.id) не считает строку с NULL.
-- Для плана без мероприятий результат равен 0.0.
SELECT p.id AS plan_id,
       u.full_name AS employee,
       p.status,
       COUNT(a.id) AS total_activities,
       COUNT(a.id) FILTER (WHERE a.status = 'completed') AS completed_activities,
       COALESCE(
           ROUND(100.0 * COUNT(a.id) FILTER (WHERE a.status = 'completed')
                 / NULLIF(COUNT(a.id), 0), 1),
           0.0
       ) AS progress_percent
FROM development_plan AS p
JOIN app_user AS u ON u.id = p.employee_id
LEFT JOIN goal AS g ON g.plan_id = p.id
LEFT JOIN activity AS a ON a.goal_id = g.id
GROUP BY p.id, u.full_name, p.status
ORDER BY p.id;

-- 3. Пользователи и текущие руководители; у верхнего руководителя NULL.
SELECT u.id, u.full_name, u.role, d.name AS department,
       m.full_name AS manager
FROM app_user AS u
JOIN department AS d ON d.id = u.department_id
LEFT JOIN app_user AS m ON m.id = u.manager_id
WHERE u.is_active = true
ORDER BY u.id;

-- 4. Очередь на согласование у руководителя с id = 3.
SELECT p.id AS plan_id, u.full_name, p.start_date, p.end_date
FROM development_plan AS p
JOIN app_user AS u ON u.id = p.employee_id
WHERE u.manager_id = 3 AND p.status = 'pending'
ORDER BY p.created_at;

-- 5. Количество активных и деактивированных пользователей.
SELECT 
    COUNT(*) FILTER (WHERE is_active = true) AS active_users,
    COUNT(*) FILTER (WHERE is_active = false) AS deactivated_users,
    COUNT(*) AS total_users
FROM app_user;