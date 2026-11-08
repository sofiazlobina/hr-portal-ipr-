--
-- PostgreSQL database dump
--

\restrict OMfLrXTHO8JPEpF0eaadqo4tO3a9cCdLMxEYwPQudcfJDqbW3evYEaIOw6EwYWY

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activity; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity (
    id integer NOT NULL,
    goal_id integer NOT NULL,
    type character varying(20) NOT NULL,
    description text NOT NULL,
    deadline date NOT NULL,
    status character varying(20) NOT NULL,
    completion_date date,
    CONSTRAINT ck_activity_completion CHECK (((((status)::text = 'completed'::text) AND (completion_date IS NOT NULL)) OR (((status)::text = 'planned'::text) AND (completion_date IS NULL)))),
    CONSTRAINT ck_activity_description CHECK ((btrim(description) <> ''::text)),
    CONSTRAINT ck_activity_status CHECK (((status)::text = ANY ((ARRAY['planned'::character varying, 'completed'::character varying])::text[]))),
    CONSTRAINT ck_activity_type CHECK (((type)::text = ANY ((ARRAY['course'::character varying, 'practice'::character varying, 'reading'::character varying])::text[])))
);


ALTER TABLE public.activity OWNER TO postgres;

--
-- Name: activity_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activity_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activity_id_seq OWNER TO postgres;

--
-- Name: activity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activity_id_seq OWNED BY public.activity.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: app_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.app_user (
    id integer NOT NULL,
    full_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    department_id integer NOT NULL,
    manager_id integer,
    is_active boolean NOT NULL,
    deactivated_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_app_user_email CHECK ((((email)::text = lower(btrim((email)::text))) AND ((email)::text <> ''::text))),
    CONSTRAINT ck_app_user_full_name CHECK ((btrim((full_name)::text) <> ''::text)),
    CONSTRAINT ck_app_user_manager CHECK (((manager_id IS NULL) OR (manager_id <> id))),
    CONSTRAINT ck_app_user_password_hash CHECK ((btrim((password_hash)::text) <> ''::text)),
    CONSTRAINT ck_app_user_role CHECK (((role)::text = ANY ((ARRAY['employee'::character varying, 'manager'::character varying, 'hr'::character varying])::text[])))
);


ALTER TABLE public.app_user OWNER TO postgres;

--
-- Name: app_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.app_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.app_user_id_seq OWNER TO postgres;

--
-- Name: app_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.app_user_id_seq OWNED BY public.app_user.id;


--
-- Name: competency; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.competency (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    CONSTRAINT ck_competency_name CHECK ((btrim((name)::text) <> ''::text))
);


ALTER TABLE public.competency OWNER TO postgres;

--
-- Name: competency_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.competency_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.competency_id_seq OWNER TO postgres;

--
-- Name: competency_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.competency_id_seq OWNED BY public.competency.id;


--
-- Name: department; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.department (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    CONSTRAINT ck_department_name CHECK ((btrim((name)::text) <> ''::text))
);


ALTER TABLE public.department OWNER TO postgres;

--
-- Name: department_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.department_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.department_id_seq OWNER TO postgres;

--
-- Name: department_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.department_id_seq OWNED BY public.department.id;


--
-- Name: development_plan; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.development_plan (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    status character varying(20) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    manager_comment text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_development_plan_dates CHECK ((end_date >= start_date)),
    CONSTRAINT ck_development_plan_rejection CHECK ((((status)::text <> 'rejected'::text) OR ((manager_comment IS NOT NULL) AND (btrim(manager_comment) <> ''::text)))),
    CONSTRAINT ck_development_plan_status CHECK (((status)::text = ANY ((ARRAY['draft'::character varying, 'pending'::character varying, 'approved'::character varying, 'rejected'::character varying, 'completed'::character varying])::text[])))
);


ALTER TABLE public.development_plan OWNER TO postgres;

--
-- Name: development_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.development_plan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.development_plan_id_seq OWNER TO postgres;

--
-- Name: development_plan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.development_plan_id_seq OWNED BY public.development_plan.id;


--
-- Name: goal; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.goal (
    id integer NOT NULL,
    plan_id integer NOT NULL,
    description text NOT NULL,
    deadline date NOT NULL,
    CONSTRAINT ck_goal_description CHECK ((btrim(description) <> ''::text))
);


ALTER TABLE public.goal OWNER TO postgres;

--
-- Name: goal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.goal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.goal_id_seq OWNER TO postgres;

--
-- Name: goal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.goal_id_seq OWNED BY public.goal.id;


--
-- Name: plan_competency; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plan_competency (
    plan_id integer NOT NULL,
    competency_id integer NOT NULL,
    current_level integer NOT NULL,
    target_level integer NOT NULL,
    CONSTRAINT ck_plan_competency_current CHECK (((current_level >= 1) AND (current_level <= 5))),
    CONSTRAINT ck_plan_competency_growth CHECK ((target_level >= current_level)),
    CONSTRAINT ck_plan_competency_target CHECK (((target_level >= 1) AND (target_level <= 5)))
);


ALTER TABLE public.plan_competency OWNER TO postgres;

--
-- Name: activity id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity ALTER COLUMN id SET DEFAULT nextval('public.activity_id_seq'::regclass);


--
-- Name: app_user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user ALTER COLUMN id SET DEFAULT nextval('public.app_user_id_seq'::regclass);


--
-- Name: competency id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competency ALTER COLUMN id SET DEFAULT nextval('public.competency_id_seq'::regclass);


--
-- Name: department id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.department ALTER COLUMN id SET DEFAULT nextval('public.department_id_seq'::regclass);


--
-- Name: development_plan id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.development_plan ALTER COLUMN id SET DEFAULT nextval('public.development_plan_id_seq'::regclass);


--
-- Name: goal id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.goal ALTER COLUMN id SET DEFAULT nextval('public.goal_id_seq'::regclass);


--
-- Data for Name: activity; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.activity (id, goal_id, type, description, deadline, status, completion_date) FROM stdin;
12	12	practice	Выполнить учебный проект	2026-11-15	planned	\N
13	13	practice	Выполнить учебный проект	2026-11-15	planned	\N
14	14	practice	Выполнить учебный проект	2026-11-15	planned	\N
15	15	practice	Выполнить учебный проект	2026-11-15	planned	\N
16	16	practice	Выполнить учебный проект	2026-11-15	completed	2026-10-25
17	17	practice	Выполнить учебный проект	2026-11-15	planned	\N
18	18	practice	Выполнить учебный проект	2026-11-15	planned	\N
19	19	practice	Выполнить учебный проект	2026-11-15	planned	\N
20	20	practice	Выполнить учебный проект	2026-11-15	planned	\N
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
f1372518e0df
\.


--
-- Data for Name: app_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.app_user (id, full_name, email, password_hash, role, department_id, manager_id, is_active, deactivated_at, created_at) FROM stdin;
16	Иванов Иван	ivanov@company.com	$2b$12$LbR03qLHKY8frG6ekq3hEeoy13sj7.VRTTVHVIBZQYCP99yLLCtw.	manager	11	\N	t	\N	2026-10-26 05:09:19.155936+07
17	Петрова Анна	petrova@company.com	$2b$12$z5hAES19cgghNP5oSpfKaOtHnLKanoR5ljp0XdAuVkMPLE/aIPfyW	employee	11	16	t	\N	2026-10-26 05:09:19.155936+07
18	Сидоров Алексей	sidorov@company.com	$2b$12$UsH3jm4u9psMAneJTg83uufLa3cfXQm1r0cD6e9wz4CqNu/A1VmNG	employee	11	16	t	\N	2026-10-26 05:09:19.155936+07
19	Козлова Мария	kozlova@company.com	$2b$12$58/UjCxntbYyCSUA3E3yQe9ZpU4GdM7UeoIBh9J8H41AX4jFiSu46	manager	12	16	t	\N	2026-10-26 05:09:19.155936+07
20	Новиков Дмитрий	novikov@company.com	$2b$12$SGeDQVBNAdq2rKBGtdk5tOQFdbVq49AusThESvjrCCPX./a47kgmC	employee	12	19	t	\N	2026-10-26 05:09:19.155936+07
21	Морозова Елена	morozova@company.com	$2b$12$YJzBBU9puLTfgD5/Sdyc3uHPgN9SD.gJcDIpDPegie3mPfZStTkau	manager	13	16	t	\N	2026-10-26 05:09:19.155936+07
22	Волков Сергей	volkov@company.com	$2b$12$jRjVy9p2lDy19iqUXt1nIOvy74iIDsj.hgs18HfuZ2JwLodZfXI5m	employee	13	21	t	\N	2026-10-26 05:09:19.155936+07
23	Соловьева Ольга	soloveva@company.com	$2b$12$0LfMLAaJxcIbrD2qL.xD5.raOEWMZJdKEgGWUq6F0AYEf9d3xvMz2	manager	14	16	t	\N	2026-10-26 05:09:19.155936+07
24	Лебедев Андрей	lebedev@company.com	$2b$12$MEjqiFza.aPrwlQJ1WQJXOr8qcW3CBgsDsBLbn5R7FL7ZWKv8qDV.	employee	14	23	t	\N	2026-10-26 05:09:19.155936+07
25	Кузнецова Татьяна	kuznetsova@company.com	$2b$12$noXu6.0fbGhrvapZnwyoOujCQnMgHdW3T50dCNXi8rI0Yoa7q0cnm	manager	15	16	t	\N	2026-10-26 05:09:19.155936+07
26	Попов Максим	popov@company.com	$2b$12$dgrT/MZ6zpb5ZUvLMlo/DOqUmBc/SlT1I3kq.ebMIjTUGT3V5LnLu	employee	15	25	t	\N	2026-10-26 05:09:19.155936+07
27	Васильева Наталья	vasileva@company.com	$2b$12$6G3fnk/9/EQo9BBpMz1OmuqPrfQS9wy/iIStan2zXQ.J2NJLUowFe	manager	16	16	t	\N	2026-10-26 05:09:19.155936+07
28	Зайцев Павел	zaytsev@company.com	$2b$12$M75403ZAEC.lcpvjQlQODeEGzh5QGj1LwFRNORAYJ/FR5jqfgFr5.	manager	17	16	t	\N	2026-10-26 05:09:19.155936+07
29	Павлова Ирина	pavlova@company.com	$2b$12$lSLQJUHreVui7ENbikXeWeEf9SXiYM7jw8GLA8tmcdjLoaUz/rulO	hr	18	16	t	\N	2026-10-26 05:09:19.155936+07
30	Семенов Виктор	semenov@company.com	$2b$12$XrcZ2npE3WD4JFrQsXVZh.ibUNMQTFbyUL5tHD7MSopoC1CtwWArC	manager	19	16	t	\N	2026-10-26 05:09:19.155936+07
\.


--
-- Data for Name: competency; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.competency (id, name, description) FROM stdin;
13	Python	\N
14	SQL	\N
15	Анализ данных	\N
16	Автотестирование	\N
17	Управление проектами	\N
18	Коммуникация	\N
19	Лидерство	\N
20	Тайм-менеджмент	\N
21	Аналитическое мышление	\N
22	Английский язык	\N
\.


--
-- Data for Name: department; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.department (id, name) FROM stdin;
11	Разработка
12	Тестирование
13	Аналитика
14	Управление проектами
15	Техническая поддержка
16	Инфраструктура
17	DevOps
18	HR
19	Финансы
20	Продажи
\.


--
-- Data for Name: development_plan; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.development_plan (id, employee_id, status, start_date, end_date, manager_comment, created_at, updated_at) FROM stdin;
13	16	approved	2026-09-26	2026-12-25	\N	2026-10-26 05:09:19.155936+07	2026-10-26 05:09:19.155936+07
14	17	draft	2026-09-26	2026-12-25	\N	2026-10-26 05:09:19.155936+07	2026-10-26 05:09:19.155936+07
15	18	pending	2026-09-26	2026-12-25	\N	2026-10-26 05:09:19.155936+07	2026-10-26 05:09:19.155936+07
16	19	approved	2026-09-26	2026-12-25	\N	2026-10-26 05:09:19.155936+07	2026-10-26 05:09:19.155936+07
17	20	completed	2026-09-26	2026-12-25	\N	2026-10-26 05:09:19.155936+07	2026-10-26 05:09:19.155936+07
18	21	approved	2026-09-26	2026-12-25	\N	2026-10-26 05:09:19.155936+07	2026-10-26 05:09:19.155936+07
19	22	draft	2026-09-26	2026-12-25	\N	2026-10-26 05:09:19.155936+07	2026-10-26 05:09:19.155936+07
20	23	rejected	2026-09-26	2026-12-25	Уточните ожидаемый результат	2026-10-26 05:09:19.155936+07	2026-10-26 05:09:19.155936+07
21	24	draft	2026-09-26	2026-12-25	\N	2026-10-26 05:09:19.155936+07	2026-10-26 05:09:19.155936+07
22	25	pending	2026-09-26	2026-12-25	\N	2026-10-26 05:09:19.155936+07	2026-10-26 05:09:19.155936+07
\.


--
-- Data for Name: goal; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.goal (id, plan_id, description, deadline) FROM stdin;
12	13	Развить практические навыки Python	2026-12-25
13	14	Развить практические навыки SQL	2026-12-25
14	15	Развить практические навыки Анализ данных	2026-12-25
15	16	Развить практические навыки Автотестирование	2026-12-25
16	17	Развить практические навыки Управление проектами	2026-12-25
17	18	Развить практические навыки Коммуникация	2026-12-25
18	19	Развить практические навыки Лидерство	2026-12-25
19	20	Развить практические навыки Тайм-менеджмент	2026-12-25
20	22	Развить практические навыки Английский язык	2026-12-25
\.


--
-- Data for Name: plan_competency; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plan_competency (plan_id, competency_id, current_level, target_level) FROM stdin;
13	13	2	4
14	14	2	4
15	15	2	4
16	16	2	4
17	17	2	4
18	18	2	4
19	19	2	4
20	20	2	4
22	22	2	4
\.


--
-- Name: activity_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.activity_id_seq', 20, true);


--
-- Name: app_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.app_user_id_seq', 30, true);


--
-- Name: competency_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.competency_id_seq', 22, true);


--
-- Name: department_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.department_id_seq', 20, true);


--
-- Name: development_plan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.development_plan_id_seq', 22, true);


--
-- Name: goal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.goal_id_seq', 20, true);


--
-- Name: activity activity_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: app_user app_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_pkey PRIMARY KEY (id);


--
-- Name: competency competency_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competency
    ADD CONSTRAINT competency_name_key UNIQUE (name);


--
-- Name: competency competency_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competency
    ADD CONSTRAINT competency_pkey PRIMARY KEY (id);


--
-- Name: department department_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT department_name_key UNIQUE (name);


--
-- Name: department department_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT department_pkey PRIMARY KEY (id);


--
-- Name: development_plan development_plan_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.development_plan
    ADD CONSTRAINT development_plan_pkey PRIMARY KEY (id);


--
-- Name: goal goal_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.goal
    ADD CONSTRAINT goal_pkey PRIMARY KEY (id);


--
-- Name: plan_competency plan_competency_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plan_competency
    ADD CONSTRAINT plan_competency_pkey PRIMARY KEY (plan_id, competency_id);


--
-- Name: idx_activity_goal; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activity_goal ON public.activity USING btree (goal_id);


--
-- Name: idx_app_user_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_app_user_active ON public.app_user USING btree (is_active);


--
-- Name: idx_app_user_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_app_user_department ON public.app_user USING btree (department_id);


--
-- Name: idx_app_user_manager; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_app_user_manager ON public.app_user USING btree (manager_id);


--
-- Name: idx_development_plan_employee; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_development_plan_employee ON public.development_plan USING btree (employee_id);


--
-- Name: idx_development_plan_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_development_plan_status ON public.development_plan USING btree (status);


--
-- Name: idx_goal_plan; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_goal_plan ON public.goal USING btree (plan_id);


--
-- Name: idx_plan_competency_competency; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_plan_competency_competency ON public.plan_competency USING btree (competency_id);


--
-- Name: ix_activity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activity_id ON public.activity USING btree (id);


--
-- Name: ix_app_user_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_app_user_email ON public.app_user USING btree (email);


--
-- Name: ix_app_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_app_user_id ON public.app_user USING btree (id);


--
-- Name: ix_competency_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_competency_id ON public.competency USING btree (id);


--
-- Name: ix_department_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_department_id ON public.department USING btree (id);


--
-- Name: ix_development_plan_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_development_plan_id ON public.development_plan USING btree (id);


--
-- Name: ix_goal_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_goal_id ON public.goal USING btree (id);


--
-- Name: activity activity_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.goal(id) ON DELETE CASCADE;


--
-- Name: app_user app_user_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.department(id);


--
-- Name: app_user app_user_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.app_user(id) ON DELETE SET NULL;


--
-- Name: development_plan development_plan_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.development_plan
    ADD CONSTRAINT development_plan_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.app_user(id);


--
-- Name: goal goal_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.goal
    ADD CONSTRAINT goal_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.development_plan(id) ON DELETE CASCADE;


--
-- Name: plan_competency plan_competency_competency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plan_competency
    ADD CONSTRAINT plan_competency_competency_id_fkey FOREIGN KEY (competency_id) REFERENCES public.competency(id);


--
-- Name: plan_competency plan_competency_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plan_competency
    ADD CONSTRAINT plan_competency_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.development_plan(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict OMfLrXTHO8JPEpF0eaadqo4tO3a9cCdLMxEYwPQudcfJDqbW3evYEaIOw6EwYWY

