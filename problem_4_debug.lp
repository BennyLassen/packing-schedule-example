\* Source Pyomo model name=PackingScheduleSimple_Problem4 *\

min 
objective:
+700 late(1)
+300 lateness(1)
+0.1 inv(1_1)
+0.1 inv(1_2)
+0.1 inv(1_3)
+0.1 inv(1_4)
+0.1 inv(1_5)
+0.1 inv(1_6)
+0.1 inv(1_7)
+0.1 inv(1_8)
+0.1 inv(1_9)
+0.1 inv(1_10)
+0.1 workforcerange
+0.1 u(1)

s.t.

c_e_one_assignment(1)_:
+1 x(1_1_1)
+1 x(1_1_2)
+1 x(1_1_3)
+1 x(1_1_4)
+1 x(1_1_5)
+1 x(1_1_6)
+1 x(1_1_7)
+1 x(1_1_8)
+1 x(1_1_9)
+1 x(1_1_10)
= 1

c_u_line_capacity(1_1)_:
-1 u(1)
+1 x(1_1_1)
<= 0

c_u_line_capacity(1_2)_:
-1 u(1)
+1 x(1_1_1)
+1 x(1_1_2)
<= 0

c_u_line_capacity(1_3)_:
-1 u(1)
+1 x(1_1_1)
+1 x(1_1_2)
+1 x(1_1_3)
<= 0

c_u_line_capacity(1_4)_:
-1 u(1)
+1 x(1_1_2)
+1 x(1_1_3)
+1 x(1_1_4)
<= 0

c_u_line_capacity(1_5)_:
-1 u(1)
+1 x(1_1_3)
+1 x(1_1_4)
+1 x(1_1_5)
<= 0

c_u_line_capacity(1_6)_:
-1 u(1)
+1 x(1_1_4)
+1 x(1_1_5)
+1 x(1_1_6)
<= 0

c_u_line_capacity(1_7)_:
-1 u(1)
+1 x(1_1_5)
+1 x(1_1_6)
+1 x(1_1_7)
<= 0

c_u_line_capacity(1_8)_:
-1 u(1)
+1 x(1_1_6)
+1 x(1_1_7)
+1 x(1_1_8)
<= 0

c_u_line_capacity(1_9)_:
-1 u(1)
+1 x(1_1_7)
+1 x(1_1_8)
+1 x(1_1_9)
<= 0

c_u_line_capacity(1_10)_:
-1 u(1)
+1 x(1_1_8)
+1 x(1_1_9)
+1 x(1_1_10)
<= 0

c_u_reserved_capacity_:
+3.0 x(1_1_1)
+3.0 x(1_1_2)
+3.0 x(1_1_3)
+3.0 x(1_1_4)
+3.0 x(1_1_5)
+3.0 x(1_1_6)
+3.0 x(1_1_7)
+3.0 x(1_1_8)
+3.0 x(1_1_9)
+3.0 x(1_1_10)
<= 9.0

c_u_line_in_use(1_1)_:
-1 u(1)
+1 x(1_1_1)
<= 0

c_u_line_in_use(1_2)_:
-1 u(1)
+1 x(1_1_1)
+1 x(1_1_2)
<= 0

c_u_line_in_use(1_3)_:
-1 u(1)
+1 x(1_1_1)
+1 x(1_1_2)
+1 x(1_1_3)
<= 0

c_u_line_in_use(1_4)_:
-1 u(1)
+1 x(1_1_2)
+1 x(1_1_3)
+1 x(1_1_4)
<= 0

c_u_line_in_use(1_5)_:
-1 u(1)
+1 x(1_1_3)
+1 x(1_1_4)
+1 x(1_1_5)
<= 0

c_u_line_in_use(1_6)_:
-1 u(1)
+1 x(1_1_4)
+1 x(1_1_5)
+1 x(1_1_6)
<= 0

c_u_line_in_use(1_7)_:
-1 u(1)
+1 x(1_1_5)
+1 x(1_1_6)
+1 x(1_1_7)
<= 0

c_u_line_in_use(1_8)_:
-1 u(1)
+1 x(1_1_6)
+1 x(1_1_7)
+1 x(1_1_8)
<= 0

c_u_line_in_use(1_9)_:
-1 u(1)
+1 x(1_1_7)
+1 x(1_1_8)
+1 x(1_1_9)
<= 0

c_u_line_in_use(1_10)_:
-1 u(1)
+1 x(1_1_8)
+1 x(1_1_9)
+1 x(1_1_10)
<= 0

c_e_ship_once(1)_:
+1 ship(1_1)
+1 ship(1_2)
+1 ship(1_3)
+1 ship(1_4)
+1 ship(1_5)
+1 ship(1_6)
+1 ship(1_7)
+1 ship(1_8)
+1 ship(1_9)
+1 ship(1_10)
= 1

c_e_shipping_time(1)_:
-1 ship(1_1)
-2 ship(1_2)
-3 ship(1_3)
-4 ship(1_4)
-5 ship(1_5)
-6 ship(1_6)
-7 ship(1_7)
-8 ship(1_8)
-9 ship(1_9)
-10 ship(1_10)
+1 timeship(1)
= 0

c_u_ship_after_complete(1)_:
-1 timeship(1)
+1 timecompletion(1)
<= 0

c_u_has_inventory_lower(1_1)_:
-1 inv(1_1)
+10000 hasinv(1_1)
<= 9999

c_u_has_inventory_lower(1_2)_:
-1 inv(1_2)
+10000 hasinv(1_2)
<= 9999

c_u_has_inventory_lower(1_3)_:
-1 inv(1_3)
+10000 hasinv(1_3)
<= 9999

c_u_has_inventory_lower(1_4)_:
-1 inv(1_4)
+10000 hasinv(1_4)
<= 9999

c_u_has_inventory_lower(1_5)_:
-1 inv(1_5)
+10000 hasinv(1_5)
<= 9999

c_u_has_inventory_lower(1_6)_:
-1 inv(1_6)
+10000 hasinv(1_6)
<= 9999

c_u_has_inventory_lower(1_7)_:
-1 inv(1_7)
+10000 hasinv(1_7)
<= 9999

c_u_has_inventory_lower(1_8)_:
-1 inv(1_8)
+10000 hasinv(1_8)
<= 9999

c_u_has_inventory_lower(1_9)_:
-1 inv(1_9)
+10000 hasinv(1_9)
<= 9999

c_u_has_inventory_lower(1_10)_:
-1 inv(1_10)
+10000 hasinv(1_10)
<= 9999

c_u_has_inventory_upper(1_1)_:
+1 inv(1_1)
-10000 hasinv(1_1)
<= 0

c_u_has_inventory_upper(1_2)_:
+1 inv(1_2)
-10000 hasinv(1_2)
<= 0

c_u_has_inventory_upper(1_3)_:
+1 inv(1_3)
-10000 hasinv(1_3)
<= 0

c_u_has_inventory_upper(1_4)_:
+1 inv(1_4)
-10000 hasinv(1_4)
<= 0

c_u_has_inventory_upper(1_5)_:
+1 inv(1_5)
-10000 hasinv(1_5)
<= 0

c_u_has_inventory_upper(1_6)_:
+1 inv(1_6)
-10000 hasinv(1_6)
<= 0

c_u_has_inventory_upper(1_7)_:
+1 inv(1_7)
-10000 hasinv(1_7)
<= 0

c_u_has_inventory_upper(1_8)_:
+1 inv(1_8)
-10000 hasinv(1_8)
<= 0

c_u_has_inventory_upper(1_9)_:
+1 inv(1_9)
-10000 hasinv(1_9)
<= 0

c_u_has_inventory_upper(1_10)_:
+1 inv(1_10)
-10000 hasinv(1_10)
<= 0

c_u_ship_requires_inventory(1_1)_:
+1 ship(1_1)
-1 hasinv(1_1)
<= 0

c_u_ship_requires_inventory(1_2)_:
+1 ship(1_2)
-1 hasinv(1_2)
<= 0

c_u_ship_requires_inventory(1_3)_:
+1 ship(1_3)
-1 hasinv(1_3)
<= 0

c_u_ship_requires_inventory(1_4)_:
+1 ship(1_4)
-1 hasinv(1_4)
<= 0

c_u_ship_requires_inventory(1_5)_:
+1 ship(1_5)
-1 hasinv(1_5)
<= 0

c_u_ship_requires_inventory(1_6)_:
+1 ship(1_6)
-1 hasinv(1_6)
<= 0

c_u_ship_requires_inventory(1_7)_:
+1 ship(1_7)
-1 hasinv(1_7)
<= 0

c_u_ship_requires_inventory(1_8)_:
+1 ship(1_8)
-1 hasinv(1_8)
<= 0

c_u_ship_requires_inventory(1_9)_:
+1 ship(1_9)
-1 hasinv(1_9)
<= 0

c_u_ship_requires_inventory(1_10)_:
+1 ship(1_10)
-1 hasinv(1_10)
<= 0

c_e_start_time(1)_:
-1 x(1_1_1)
-2 x(1_1_2)
-3 x(1_1_3)
-4 x(1_1_4)
-5 x(1_1_5)
-6 x(1_1_6)
-7 x(1_1_7)
-8 x(1_1_8)
-9 x(1_1_9)
-10 x(1_1_10)
+1 timestart(1)
= 0

c_e_completion_time(1)_:
-4.0 x(1_1_1)
-5.0 x(1_1_2)
-6.0 x(1_1_3)
-7.0 x(1_1_4)
-8.0 x(1_1_5)
-9.0 x(1_1_6)
-10.0 x(1_1_7)
-11.0 x(1_1_8)
-12.0 x(1_1_9)
-13.0 x(1_1_10)
+1 timecompletion(1)
= 0

c_e_flow_time(1)_:
-1 timeship(1)
+1 timestart(1)
+1 timeflow(1)
= 0

c_e_production(1_1)_:
+1 prod(1_1)
= 0

c_e_production(1_2)_:
+1 prod(1_2)
= 0

c_e_production(1_3)_:
+1 prod(1_3)
= 0

c_e_production(1_4)_:
-1 x(1_1_1)
+1 prod(1_4)
= 0

c_e_production(1_5)_:
-1 x(1_1_2)
+1 prod(1_5)
= 0

c_e_production(1_6)_:
-1 x(1_1_3)
+1 prod(1_6)
= 0

c_e_production(1_7)_:
-1 x(1_1_4)
+1 prod(1_7)
= 0

c_e_production(1_8)_:
-1 x(1_1_5)
+1 prod(1_8)
= 0

c_e_production(1_9)_:
-1 x(1_1_6)
+1 prod(1_9)
= 0

c_e_production(1_10)_:
-1 x(1_1_7)
+1 prod(1_10)
= 0

c_e_inventory_balance(1_1)_:
-1 inv(1_0)
+1 inv(1_1)
+1 ship(1_1)
-1 prod(1_1)
= 0

c_e_inventory_balance(1_2)_:
-1 inv(1_1)
+1 inv(1_2)
+1 ship(1_2)
-1 prod(1_2)
= 0

c_e_inventory_balance(1_3)_:
-1 inv(1_2)
+1 inv(1_3)
+1 ship(1_3)
-1 prod(1_3)
= 0

c_e_inventory_balance(1_4)_:
-1 inv(1_3)
+1 inv(1_4)
+1 ship(1_4)
-1 prod(1_4)
= 0

c_e_inventory_balance(1_5)_:
-1 inv(1_4)
+1 inv(1_5)
+1 ship(1_5)
-1 prod(1_5)
= 0

c_e_inventory_balance(1_6)_:
-1 inv(1_5)
+1 inv(1_6)
+1 ship(1_6)
-1 prod(1_6)
= 0

c_e_inventory_balance(1_7)_:
-1 inv(1_6)
+1 inv(1_7)
+1 ship(1_7)
-1 prod(1_7)
= 0

c_e_inventory_balance(1_8)_:
-1 inv(1_7)
+1 inv(1_8)
+1 ship(1_8)
-1 prod(1_8)
= 0

c_e_inventory_balance(1_9)_:
-1 inv(1_8)
+1 inv(1_9)
+1 ship(1_9)
-1 prod(1_9)
= 0

c_e_inventory_balance(1_10)_:
-1 inv(1_9)
+1 inv(1_10)
+1 ship(1_10)
-1 prod(1_10)
= 0

c_e_initial_inventory(1)_:
+1 inv(1_0)
= 0

c_e_workers_used(1)_:
-1 x(1_1_1)
+1 workersused(1)
= 0

c_e_workers_used(2)_:
-1 x(1_1_1)
-1 x(1_1_2)
+1 workersused(2)
= 0

c_e_workers_used(3)_:
-1 x(1_1_1)
-1 x(1_1_2)
-1 x(1_1_3)
+1 workersused(3)
= 0

c_e_workers_used(4)_:
-1 x(1_1_2)
-1 x(1_1_3)
-1 x(1_1_4)
+1 workersused(4)
= 0

c_e_workers_used(5)_:
-1 x(1_1_3)
-1 x(1_1_4)
-1 x(1_1_5)
+1 workersused(5)
= 0

c_e_workers_used(6)_:
-1 x(1_1_4)
-1 x(1_1_5)
-1 x(1_1_6)
+1 workersused(6)
= 0

c_e_workers_used(7)_:
-1 x(1_1_5)
-1 x(1_1_6)
-1 x(1_1_7)
+1 workersused(7)
= 0

c_e_workers_used(8)_:
-1 x(1_1_6)
-1 x(1_1_7)
-1 x(1_1_8)
+1 workersused(8)
= 0

c_e_workers_used(9)_:
-1 x(1_1_7)
-1 x(1_1_8)
-1 x(1_1_9)
+1 workersused(9)
= 0

c_e_workers_used(10)_:
-1 x(1_1_8)
-1 x(1_1_9)
-1 x(1_1_10)
+1 workersused(10)
= 0

c_u_max_workforce(1)_:
+1 workersused(1)
-1 workersmax
<= 0

c_u_max_workforce(2)_:
+1 workersused(2)
-1 workersmax
<= 0

c_u_max_workforce(3)_:
+1 workersused(3)
-1 workersmax
<= 0

c_u_max_workforce(4)_:
+1 workersused(4)
-1 workersmax
<= 0

c_u_max_workforce(5)_:
+1 workersused(5)
-1 workersmax
<= 0

c_u_max_workforce(6)_:
+1 workersused(6)
-1 workersmax
<= 0

c_u_max_workforce(7)_:
+1 workersused(7)
-1 workersmax
<= 0

c_u_max_workforce(8)_:
+1 workersused(8)
-1 workersmax
<= 0

c_u_max_workforce(9)_:
+1 workersused(9)
-1 workersmax
<= 0

c_u_max_workforce(10)_:
+1 workersused(10)
-1 workersmax
<= 0

c_u_min_workforce(1)_:
-1 workersused(1)
+1 workersmin
<= 0

c_u_min_workforce(2)_:
-1 workersused(2)
+1 workersmin
<= 0

c_u_min_workforce(3)_:
-1 workersused(3)
+1 workersmin
<= 0

c_u_min_workforce(4)_:
-1 workersused(4)
+1 workersmin
<= 0

c_u_min_workforce(5)_:
-1 workersused(5)
+1 workersmin
<= 0

c_u_min_workforce(6)_:
-1 workersused(6)
+1 workersmin
<= 0

c_u_min_workforce(7)_:
-1 workersused(7)
+1 workersmin
<= 0

c_u_min_workforce(8)_:
-1 workersused(8)
+1 workersmin
<= 0

c_u_min_workforce(9)_:
-1 workersused(9)
+1 workersmin
<= 0

c_u_min_workforce(10)_:
-1 workersused(10)
+1 workersmin
<= 0

c_e_workforce_range_:
+1 workforcerange
-1 workersmax
+1 workersmin
= 0

bounds
   0 <= late(1) <= 1
   0 <= lateness(1) <= +inf
   0 <= inv(1_0) <= +inf
   0 <= inv(1_1) <= +inf
   0 <= inv(1_2) <= +inf
   0 <= inv(1_3) <= +inf
   0 <= inv(1_4) <= +inf
   0 <= inv(1_5) <= +inf
   0 <= inv(1_6) <= +inf
   0 <= inv(1_7) <= +inf
   0 <= inv(1_8) <= +inf
   0 <= inv(1_9) <= +inf
   0 <= inv(1_10) <= +inf
   0 <= workforcerange <= 1
   0 <= u(1) <= 1
   0 <= x(1_1_1) <= 1
   0 <= x(1_1_2) <= 1
   0 <= x(1_1_3) <= 1
   0 <= x(1_1_4) <= 1
   0 <= x(1_1_5) <= 1
   0 <= x(1_1_6) <= 1
   0 <= x(1_1_7) <= 1
   0 <= x(1_1_8) <= 1
   0 <= x(1_1_9) <= 1
   0 <= x(1_1_10) <= 1
   0 <= ship(1_1) <= 1
   0 <= ship(1_2) <= 1
   0 <= ship(1_3) <= 1
   0 <= ship(1_4) <= 1
   0 <= ship(1_5) <= 1
   0 <= ship(1_6) <= 1
   0 <= ship(1_7) <= 1
   0 <= ship(1_8) <= 1
   0 <= ship(1_9) <= 1
   0 <= ship(1_10) <= 1
   1 <= timeship(1) <= 10
   1 <= timecompletion(1) <= 10
   0 <= hasinv(1_1) <= 1
   0 <= hasinv(1_2) <= 1
   0 <= hasinv(1_3) <= 1
   0 <= hasinv(1_4) <= 1
   0 <= hasinv(1_5) <= 1
   0 <= hasinv(1_6) <= 1
   0 <= hasinv(1_7) <= 1
   0 <= hasinv(1_8) <= 1
   0 <= hasinv(1_9) <= 1
   0 <= hasinv(1_10) <= 1
   1 <= timestart(1) <= 10
   0 <= timeflow(1) <= +inf
   0 <= prod(1_1) <= +inf
   0 <= prod(1_2) <= +inf
   0 <= prod(1_3) <= +inf
   0 <= prod(1_4) <= +inf
   0 <= prod(1_5) <= +inf
   0 <= prod(1_6) <= +inf
   0 <= prod(1_7) <= +inf
   0 <= prod(1_8) <= +inf
   0 <= prod(1_9) <= +inf
   0 <= prod(1_10) <= +inf
   0 <= workersused(1) <= 1
   0 <= workersused(2) <= 1
   0 <= workersused(3) <= 1
   0 <= workersused(4) <= 1
   0 <= workersused(5) <= 1
   0 <= workersused(6) <= 1
   0 <= workersused(7) <= 1
   0 <= workersused(8) <= 1
   0 <= workersused(9) <= 1
   0 <= workersused(10) <= 1
   0 <= workersmax <= 1
   0 <= workersmin <= 1
general
  lateness(1)
  inv(1_0)
  inv(1_1)
  inv(1_2)
  inv(1_3)
  inv(1_4)
  inv(1_5)
  inv(1_6)
  inv(1_7)
  inv(1_8)
  inv(1_9)
  inv(1_10)
  workforcerange
  timeship(1)
  timecompletion(1)
  timestart(1)
  timeflow(1)
  prod(1_1)
  prod(1_2)
  prod(1_3)
  prod(1_4)
  prod(1_5)
  prod(1_6)
  prod(1_7)
  prod(1_8)
  prod(1_9)
  prod(1_10)
  workersused(1)
  workersused(2)
  workersused(3)
  workersused(4)
  workersused(5)
  workersused(6)
  workersused(7)
  workersused(8)
  workersused(9)
  workersused(10)
  workersmax
  workersmin
binary
  late(1)
  u(1)
  x(1_1_1)
  x(1_1_2)
  x(1_1_3)
  x(1_1_4)
  x(1_1_5)
  x(1_1_6)
  x(1_1_7)
  x(1_1_8)
  x(1_1_9)
  x(1_1_10)
  ship(1_1)
  ship(1_2)
  ship(1_3)
  ship(1_4)
  ship(1_5)
  ship(1_6)
  ship(1_7)
  ship(1_8)
  ship(1_9)
  ship(1_10)
  hasinv(1_1)
  hasinv(1_2)
  hasinv(1_3)
  hasinv(1_4)
  hasinv(1_5)
  hasinv(1_6)
  hasinv(1_7)
  hasinv(1_8)
  hasinv(1_9)
  hasinv(1_10)
end
