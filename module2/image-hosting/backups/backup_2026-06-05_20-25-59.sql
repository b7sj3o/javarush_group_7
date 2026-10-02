--
-- PostgreSQL database dump
--

\restrict dDyCtoZxdDEPLrtRKca8q9IQH77sqqvJ2gSHrmnMcNNNhkLM3ilWxeZSdVfbgwz

-- Dumped from database version 17.10 (Debian 17.10-1.pgdg13+1)
-- Dumped by pg_dump version 17.10 (Debian 17.10-1.pgdg13+1)

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
-- Name: images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.images (
    id integer NOT NULL,
    filename text NOT NULL,
    original_name text NOT NULL,
    size integer NOT NULL,
    upload_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    file_type text NOT NULL
);


ALTER TABLE public.images OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.images_id_seq OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.images_id_seq OWNED BY public.images.id;


--
-- Name: images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images ALTER COLUMN id SET DEFAULT nextval('public.images_id_seq'::regclass);


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.images (id, filename, original_name, size, upload_time, file_type) FROM stdin;
8	cedcf840-feba-453a-893a-fca01728bcee.png	Мандрівники.png	149163	2026-06-02 17:03:36.385684	png
9	adfd2625-224b-4e50-b0b9-964d1f1e3246.png	Дизайн без назви (4).png	1073150	2026-06-02 17:05:35.679794	png
12	8396e15e-ec0a-40f0-8ff3-6c4be2828db9.png	Frame 61 (1).png	2627417	2026-06-02 17:40:36.236741	png
13	eca33467-0232-46b2-a7a9-596ee47c0de3.png	Frame 62 (1).png	2670692	2026-06-02 17:40:37.863747	png
14	70255cdb-6401-4443-8a4f-645baa3944c6.jpg	1_final.jpg	1288228	2026-06-02 17:40:40.324985	jpg
15	072d3f11-5cca-4bda-836e-25326e6701d6.jpg	2_final.jpg	1302702	2026-06-02 17:40:42.154905	jpg
16	c744b765-84da-42ee-91fe-2b71e20a7c6c.jpg	3_final.jpg	1082155	2026-06-02 17:40:44.226796	jpg
17	7e2c7e30-a52f-4ffe-bb2e-c6c47befa177.jpg	6_final.jpg	3951894	2026-06-02 17:40:46.081254	jpg
18	8d8377de-d902-42fb-9280-543c38c559a5.png	Мандрівники.png	149163	2026-06-02 17:40:47.76745	png
19	d4ec9729-3376-4cd7-9bef-325b54811ace.png	image_2026-05-14_22-30-57.png	22739	2026-06-02 17:40:50.345239	png
20	cd9ce2c5-6119-4447-8e18-d1dfb332fa03.png	image_2026-05-14_22-28-18.png	17184	2026-06-02 17:40:52.521445	png
21	a47f661f-ce03-417b-a41c-fd59260befba.png	Frame 58 (1).png	188034	2026-06-02 17:40:54.240223	png
22	bd128c8b-1fa8-485a-a101-2aad6b69d182.png	Frame 58 (2).png	2415633	2026-06-02 17:40:56.46009	png
23	6512b7eb-a67c-47bf-af89-8d3717e3f288.jpg	2_final.jpg	1302702	2026-06-02 17:41:07.390147	jpg
24	b0cbb020-a771-462c-a31b-c65b8c2dbbb7.png	image_2026-05-14_22-27-52.png	8839	2026-06-02 17:41:09.175209	png
25	1a29c41b-271d-4ae5-98cf-c3ba367788b0.png	image_2026-05-27_00-25-42.png	751213	2026-06-02 17:41:11.579865	png
26	49d1b7c4-51a9-4caf-9797-851f889bffd2.png	Frame 62 (1).png	2670692	2026-06-02 17:41:13.464177	png
27	16cdbd71-d5d9-441c-89ce-3de9a88ef685.png	Frame 58 (1) (2).png	188034	2026-06-02 17:41:14.936407	png
28	f5664c31-00d7-4d9e-a2fa-e2114df541ce.png	Frame 61 (1).png	2627417	2026-06-05 16:27:47.770743	png
\.


--
-- Name: images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.images_id_seq', 28, true);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

\unrestrict dDyCtoZxdDEPLrtRKca8q9IQH77sqqvJ2gSHrmnMcNNNhkLM3ilWxeZSdVfbgwz

