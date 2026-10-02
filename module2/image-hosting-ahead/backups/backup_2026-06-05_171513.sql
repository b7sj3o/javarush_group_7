--
-- PostgreSQL database dump
--

\restrict xjQqM6dyltPkxdWuVTHf8SPnu3lIu9P0fmcfDcQ91ysd4QsQa43Gy2edKA5qRVM

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
1	a1b2c3d4.jpg	sunset.jpg	245000	2026-05-25 11:52:43.023207	jpg
2	e5f6g7h8.png	cat-meme.png	1200000	2026-05-25 11:52:43.023207	png
3	i9j0k1l2.gif	dancing.gif	800000	2026-05-25 11:52:43.023207	gif
4	m3n4o5p6.jpg	landscape.jpg	3500000	2026-05-25 11:52:43.023207	jpg
5	q7r8s9t0.png	screenshot.png	567000	2026-05-25 11:52:43.023207	png
6	f2607a91-4708-4919-a4a7-48ecf4639d44.png	d133566d065a59853b916645fb366ad236f1dfbc.png	164731	2026-06-02 15:58:50.450799	png
\.


--
-- Name: images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.images_id_seq', 6, true);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

\unrestrict xjQqM6dyltPkxdWuVTHf8SPnu3lIu9P0fmcfDcQ91ysd4QsQa43Gy2edKA5qRVM

