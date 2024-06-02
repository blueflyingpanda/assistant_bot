CREATE TABLE "users"
(
    "id"       integer PRIMARY KEY,
    "tg_id"    integer UNIQUE NOT NULL,
    "username" varchar        NOT NULL,
    "name"     varchar,
    "phone"    varchar,
    "group_id" integer
);

CREATE TABLE "groups"
(
    "id"    integer PRIMARY KEY,
    "title" varchar UNIQUE NOT NULL,
    "year"  integer        NOT NULL
);

CREATE TABLE "courses"
(
    "id"          integer PRIMARY KEY,
    "title"       varchar,
    "year"        integer,
    "teachers"    int,
    "exam_weight" int
);

CREATE TABLE "lessons"
(
    "id"        integer PRIMARY KEY,
    "title"     varchar,
    "type"      int,
    "date"      date,
    "course_id" int
);

CREATE TABLE "attendances"
(
    "id"            integer PRIMARY KEY,
    "user_id"       integer,
    "lesson_id"     integer,
    "grade"         integer,
    "participation" bool DEFAULT false
);

COMMENT ON TABLE "groups" IS 'на случай если на курсе несколько групп и один чат';

COMMENT ON COLUMN "groups"."year" IS '1-4';

COMMENT ON COLUMN "courses"."exam_weight" IS 'вес экзамена от общей оценки в процентах';

COMMENT ON COLUMN "lessons"."type" IS '0-lecture 1-lab 2-seminar';

ALTER TABLE "users"
    ADD FOREIGN KEY ("group_id") REFERENCES "groups" ("id");

ALTER TABLE "lessons"
    ADD FOREIGN KEY ("course_id") REFERENCES "courses" ("id");

ALTER TABLE "attendances"
    ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "attendances"
    ADD FOREIGN KEY ("lesson_id") REFERENCES "lessons" ("id");

CREATE TABLE "users_courses"
(
    "users_id"   integer,
    "courses_id" integer,
    "teacher"    boolean DEFAULT false,
    PRIMARY KEY ("users_id", "courses_id")
);

ALTER TABLE "users_courses"
    ADD FOREIGN KEY ("users_id") REFERENCES "users" ("id");

ALTER TABLE "users_courses"
    ADD FOREIGN KEY ("courses_id") REFERENCES "courses" ("id");
