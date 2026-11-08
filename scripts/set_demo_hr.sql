-- Только для старого демонстрационного наполнения, где Павлова ошибочно manager.
-- Выполнить в своей базе после резервного копирования.
BEGIN;
UPDATE app_user SET role = 'hr' WHERE email = 'pavlova@company.com';
COMMIT;
SELECT id, email, role FROM app_user WHERE email = 'pavlova@company.com';
