\* Source Pyomo model name=PackingSchedule_Problem4_1_c2 *\

min 
objective:
+1 inv(1_1)

s.t.

c_u_one_assignment(1)_:
+1 x(1_1)
<= 1

c_e_processing_time(1)_:
-10.0 x(1_1)
+1 complete(1)
-1 start(1)
= 0

c_l_start_time_nonneg(1)_:
+1 start(1)
>= 0

c_u_completion_within_horizon(1)_:
+1 complete(1)
<= 50.0

c_e_track_produced_items(1_1)_:
+1 prodbefore(1_1)
-1 prodorder(1_1)
= 0

c_u_order_before_shipping(1_1)_:
+1 complete(1)
+500.0 prodorder(1_1)
-1 ship(1)
<= 500.0

c_u_order_after_shipping(1_1)_:
-1 complete(1)
-500.0 prodorder(1_1)
+1 ship(1)
<= -0.01

c_u_ship_within_horizon(1)_:
+1 ship(1)
<= 50.0

c_l_ship_no_earlier_than_due(1)_:
+1 ship(1)
>= 15.0

c_e_inventory_balance(1_1)_:
+1 inv(1_1)
-1 prodbefore(1_1)
+1 shipped(1_1)
= 0

c_l_inventory_nonnegative(1_1)_:
+1 inv(1_1)
>= 0

c_u_shipped_before(1_1)_:
+500.0 shipped(1_1)
<= 500.0

c_u_shipped_after(1_1)_:
-500.0 shipped(1_1)
<= -0.01

c_e_event_time_start(1)_:
-1 start(1)
+1 t_event(1)
= 0

c_e_event_time_completion(1)_:
-1 complete(1)
+1 t_event(2)
= 0

c_u_active_constraint_1(1_1)_:
+1 is_active(1_1)
-1 started(1_1)
<= 0

c_u_active_constraint_1(1_2)_:
+1 is_active(1_2)
-1 started(1_2)
<= 0

c_u_active_constraint_2(1_1)_:
+1 is_active(1_1)
-1 notcomplete(1_1)
<= 0

c_u_active_constraint_2(1_2)_:
+1 is_active(1_2)
-1 notcomplete(1_2)
<= 0

c_u_active_constraint_3(1_1)_:
-1 is_active(1_1)
+1 started(1_1)
+1 notcomplete(1_1)
<= 1

c_u_active_constraint_3(1_2)_:
-1 is_active(1_2)
+1 started(1_2)
+1 notcomplete(1_2)
<= 1

c_u_started_true(1_1)_:
+1 start(1)
-1 t_event(1)
+500.0 started(1_1)
<= 500.0

c_u_started_true(1_2)_:
+1 start(1)
-1 t_event(2)
+500.0 started(1_2)
<= 500.0

c_u_started_false(1_1)_:
-1 start(1)
+1 t_event(1)
-500.0 started(1_1)
<= -0.01

c_u_started_false(1_2)_:
-1 start(1)
+1 t_event(2)
-500.0 started(1_2)
<= -0.01

c_u_notcomplete_true(1_1)_:
-1 complete(1)
+1 t_event(1)
+500.0 notcomplete(1_1)
<= 499.99

c_u_notcomplete_true(1_2)_:
-1 complete(1)
+1 t_event(2)
+500.0 notcomplete(1_2)
<= 499.99

c_u_notcomplete_false(1_1)_:
+1 complete(1)
-1 t_event(1)
-500.0 notcomplete(1_1)
<= 0

c_u_notcomplete_false(1_2)_:
+1 complete(1)
-1 t_event(2)
-500.0 notcomplete(1_2)
<= 0

c_e_workers_used(1)_:
-1 is_active(1_1)
+1 workersused(1)
= 0

c_e_workers_used(2)_:
-1 is_active(1_2)
+1 workersused(2)
= 0

c_u_max_workforce(1)_:
+1 workersused(1)
-1 workersmax
<= 0

c_u_max_workforce(2)_:
+1 workersused(2)
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

c_e_workforce_range_:
-1 workersmax
+1 workersmin
+1 workforcerange
= 0

bounds
   0 <= inv(1_1) <= +inf
   0 <= x(1_1) <= 1
   0 <= complete(1) <= 50.0
   0 <= start(1) <= 50.0
   0 <= prodbefore(1_1) <= +inf
   0 <= prodorder(1_1) <= 1
   0 <= ship(1) <= 50.0
   0 <= shipped(1_1) <= 1
   0 <= t_event(1) <= 50.0
   0 <= t_event(2) <= 50.0
   0 <= is_active(1_1) <= 1
   0 <= is_active(1_2) <= 1
   0 <= started(1_1) <= 1
   0 <= started(1_2) <= 1
   0 <= notcomplete(1_1) <= 1
   0 <= notcomplete(1_2) <= 1
   0 <= workersused(1) <= 1
   0 <= workersused(2) <= 1
   0 <= workersmax <= 1
   0 <= workersmin <= 1
   0 <= workforcerange <= 1
general
  inv(1_1)
  prodbefore(1_1)
binary
  x(1_1)
  prodorder(1_1)
  shipped(1_1)
  is_active(1_1)
  is_active(1_2)
  started(1_1)
  started(1_2)
  notcomplete(1_1)
  notcomplete(1_2)
end
