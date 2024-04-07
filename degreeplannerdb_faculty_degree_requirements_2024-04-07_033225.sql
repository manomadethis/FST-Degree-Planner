--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1
-- Dumped by pg_dump version 16.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: faculty_degree_requirements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.faculty_degree_requirements (
    faculty_name character varying(50) NOT NULL PRIMARY KEY,
    level_1_credits_required character varying(2) NOT NULL,
    advanced_credits_required character varying(2) NOT NULL,
    foundation_credits_required character varying(2) NOT NULL,
    notes text NOT NULL
);


ALTER TABLE public.faculty_degree_requirements OWNER TO postgres;

--
-- Data for Name: faculty_degree_requirements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.faculty_degree_requirements (level_1_credits_required, advanced_credits_required, foundation_credits_required, notes) FROM stdin;
24	60	9	Eighteen (18) Level 1 credits must be from FST courses.\n\nAll courses relating to the declared major(s) and or minor(s) must be completed\n\nThree (3) FOUN courses required for FST Students: 1. Either FOUN1014: Critical Reading and Writing in Science and Technology & Medical Science or FOUN1019: Critical Reading and Writing in the Disciplines 2. FOUN1101: Caribbean Civilization* 3. FOUN1301: Law, Governance, Economy and Society*\n\nStudents may now substitute one (1) Foundation course (except for English Language/Writing courses) with a foreign language at the level of their competence. They may choose from any modern language, Caribbean sign language or Caribbean vernacular language course. Exemptions may also be granted from time to time by the Board for Undergraduate Studies.
\.


--
-- PostgreSQL database dump complete
--

