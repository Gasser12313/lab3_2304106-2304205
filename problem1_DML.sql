
USE company;


INSERT INTO employee (ssn, fname, lname, bdate, address, gender, salary, Dno) VALUES
('111223333', 'Ahmed',   'Hassan', '1985-03-14', '12 Fouad St, Alexandria',    'M',  9500.00, NULL),
('222334444', 'Mona',    'Adel',   '1990-07-22', '5 Sidi Gaber, Alexandria',   'F',  8200.00, NULL),
('333445555', 'Omar',    'Khaled', '1982-11-05', '48 Smouha, Alexandria',      'M', 12000.00, NULL),
('444556666', 'Sara',    'Mahmoud','1995-01-30', '9 Miami, Alexandria',        'F',  7000.00, NULL),
('555667777', 'Youssef', 'Ali',    '1988-09-17', '77 Stanley, Alexandria',     'M', 10500.00, NULL);


INSERT INTO department (Dnumber, Dname, mgr_ssn, mgr_start_date) VALUES
(1, 'Headquarters',   '555667777', '2015-06-01'),
(2, 'Research',       '333445555', '2018-02-15'),
(3, 'Administration', '222334444', '2020-09-01');


UPDATE employee SET Dno = 2 WHERE ssn = '111223333';
UPDATE employee SET Dno = 3 WHERE ssn = '222334444';
UPDATE employee SET Dno = 2 WHERE ssn = '333445555';
UPDATE employee SET Dno = 3 WHERE ssn = '444556666';
UPDATE employee SET Dno = 1 WHERE ssn = '555667777';


INSERT INTO project (Pnumber, Pname, Plocation, Dno) VALUES
(10, 'Website Redesign', 'Alexandria', 2),
(20, 'Data Warehouse',   'Cairo',      2),
(30, 'Office Move',      'Alexandria', 1),
(40, 'Payroll System',   'Alexandria', 3);
