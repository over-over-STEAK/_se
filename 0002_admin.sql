-- Existing data is preserved. A student has one grade per course name and term.
CREATE UNIQUE INDEX grades_student_course_term ON grades(user_id,name,term);
CREATE TRIGGER course_update_checks BEFORE UPDATE ON courses BEGIN
 SELECT CASE WHEN NEW.capacity<(SELECT count(*) FROM enrollments WHERE course_id=OLD.id) THEN RAISE(ABORT,'capacity_below_enrolled') END;
 SELECT CASE WHEN EXISTS(SELECT 1 FROM enrollments WHERE course_id=OLD.id) AND (NEW.day<>OLD.day OR NEW.period<>OLD.period OR NEW.credits<>OLD.credits) THEN RAISE(ABORT,'occupied_schedule_locked') END;
END;
CREATE TRIGGER course_delete_checks BEFORE DELETE ON courses BEGIN
 SELECT CASE WHEN EXISTS(SELECT 1 FROM enrollments WHERE course_id=OLD.id) THEN RAISE(ABORT,'course_has_students') END;
END;
