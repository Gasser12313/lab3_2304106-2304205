
DROP DATABASE IF EXISTS company;
CREATE DATABASE company;
USE company;


CREATE TABLE employee (
    ssn     CHAR(9)       NOT NULL,
    fname   VARCHAR(30)   NOT NULL,
    lname   VARCHAR(30)   NOT NULL,
    bdate   DATE,
    address VARCHAR(100),
    gender  CHAR(1),
    salary  DECIMAL(10,2),
    Dno     INT,
    PRIMARY KEY (ssn)
);

CREATE TABLE department (
    Dnumber        INT         NOT NULL,
    Dname          VARCHAR(50) NOT NULL,
    mgr_ssn        CHAR(9),
    mgr_start_date DATE,
    PRIMARY KEY (Dnumber)
);

CREATE TABLE project (
    Pnumber   INT         NOT NULL,
    Pname     VARCHAR(50) NOT NULL,
    Plocation VARCHAR(50),
    Dno       INT         NOT NULL,
    PRIMARY KEY (Pnumber)
);


ALTER TABLE employee   ADD CONSTRAINT fk_emp_dept     FOREIGN KEY (Dno)     REFERENCES department (Dnumber);
ALTER TABLE department ADD CONSTRAINT fk_dept_mgr     FOREIGN KEY (mgr_ssn) REFERENCES employee (ssn);
ALTER TABLE project    ADD CONSTRAINT fk_project_dept FOREIGN KEY (Dno)     REFERENCES department (Dnumber);
