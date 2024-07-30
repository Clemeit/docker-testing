CREATE TABLE IF NOT EXISTS public."character"
(
    id bigint NOT NULL,
    name character varying(20) COLLATE pg_catalog."default",
    gender character varying(10) COLLATE pg_catalog."default",
    race character varying(25) COLLATE pg_catalog."default" NOT NULL,
    total_level smallint NOT NULL,
    classes jsonb NOT NULL,
    guild_name character varying(25) COLLATE pg_catalog."default",
    location bigint NOT NULL,
    server_name character varying(20) COLLATE pg_catalog."default" NOT NULL,
    home_server_name character varying(20) COLLATE pg_catalog."default",
    group_id bigint,
    is_anonymous boolean NOT NULL,
    is_recruiting boolean NOT NULL,
    metadata bigint,
    CONSTRAINT character_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."character"
    OWNER to pgadmin;