-- ================================================================
-- SEED DATA FOR SUPABASE - SPA/SALON SYSTEM (FIXED)
-- ================================================================
-- Run this AFTER the schema is created
-- Fixed: Proper TIME type casting for staff availability
-- ================================================================

-- ================================================================
-- SERVICE CATEGORIES
-- ================================================================

INSERT INTO service_categories (name, description, display_order) VALUES
    ('Hair Services', 'Cuts, color, styling for all hair types', 1),
    ('Spa & Massage', 'Relaxation and therapeutic massage services', 2),
    ('Skincare & Facials', 'Professional facial treatments and skincare', 3),
    ('Nails', 'Manicures, pedicures, and nail art', 4),
    ('Body Treatments', 'Waxing, body wraps, and exfoliation', 5),
    ('Makeup & Lashes', 'Professional makeup application and lash services', 6)
ON CONFLICT (name) DO NOTHING;

-- ================================================================
-- SERVICES
-- ================================================================

DO $$
DECLARE
    hair_id UUID;
    spa_id UUID;
    skin_id UUID;
    nails_id UUID;
    body_id UUID;
    makeup_id UUID;
BEGIN
    SELECT id INTO hair_id FROM service_categories WHERE name = 'Hair Services';
    SELECT id INTO spa_id FROM service_categories WHERE name = 'Spa & Massage';
    SELECT id INTO skin_id FROM service_categories WHERE name = 'Skincare & Facials';
    SELECT id INTO nails_id FROM service_categories WHERE name = 'Nails';
    SELECT id INTO body_id FROM service_categories WHERE name = 'Body Treatments';
    SELECT id INTO makeup_id FROM service_categories WHERE name = 'Makeup & Lashes';

    -- Hair Services
    INSERT INTO services (category_id, name, description, duration_minutes, base_price, member_price, display_order) VALUES
        (hair_id, 'Women''s Haircut', 'Precision cut with style consultation', 60, 75.00, 68.00, 1),
        (hair_id, 'Men''s Haircut', 'Classic cut with neck cleanup', 45, 45.00, 40.00, 2),
        (hair_id, 'Blowout & Style', 'Professional blow-dry and styling', 45, 55.00, 50.00, 3),
        (hair_id, 'Full Highlights', 'Traditional foil highlights', 150, 185.00, 165.00, 4),
        (hair_id, 'Balayage', 'Hand-painted dimensional color', 180, 225.00, 200.00, 5),
        (hair_id, 'Single Process Color', 'All-over color application', 90, 95.00, 85.00, 6);

    -- Spa & Massage
    INSERT INTO services (category_id, name, description, duration_minutes, base_price, member_price, display_order) VALUES
        (spa_id, 'Swedish Massage - 60 min', 'Relaxing full-body massage', 60, 95.00, 85.00, 1),
        (spa_id, 'Deep Tissue Massage - 60 min', 'Therapeutic muscle relief', 60, 110.00, 100.00, 2),
        (spa_id, 'Hot Stone Massage', 'Heated stones for deep relaxation', 90, 145.00, 130.00, 3),
        (spa_id, 'Couples Massage', 'Side-by-side massage for two', 60, 220.00, 200.00, 4),
        (spa_id, 'Aromatherapy Massage', 'Massage with essential oils', 75, 125.00, 110.00, 5);

    -- Skincare & Facials
    INSERT INTO services (category_id, name, description, duration_minutes, base_price, member_price, display_order) VALUES
        (skin_id, 'Classic Facial', 'Deep cleanse, exfoliation, mask', 60, 95.00, 85.00, 1),
        (skin_id, 'Anti-Aging Facial', 'Peptides and retinol treatment', 75, 135.00, 120.00, 2),
        (skin_id, 'Microdermabrasion', 'Exfoliation and skin renewal', 60, 145.00, 130.00, 3),
        (skin_id, 'Chemical Peel', 'Professional skin resurfacing', 45, 165.00, 150.00, 4),
        (skin_id, 'Hydrating Facial', 'Intense moisture restoration', 60, 105.00, 95.00, 5);

    -- Nails
    INSERT INTO services (category_id, name, description, duration_minutes, base_price, member_price, display_order) VALUES
        (nails_id, 'Classic Manicure', 'Shape, buff, polish', 45, 35.00, 32.00, 1),
        (nails_id, 'Gel Manicure', 'Long-lasting gel polish', 60, 55.00, 50.00, 2),
        (nails_id, 'Classic Pedicure', 'Soak, scrub, polish', 60, 55.00, 50.00, 3),
        (nails_id, 'Spa Pedicure', 'Ultimate foot treatment', 90, 95.00, 85.00, 4),
        (nails_id, 'Acrylic Full Set', 'Sculptured acrylic nails', 90, 65.00, 60.00, 5);

    -- Body Treatments
    INSERT INTO services (category_id, name, description, duration_minutes, base_price, member_price, display_order) VALUES
        (body_id, 'Eyebrow Wax', 'Shape and clean brows', 15, 20.00, 18.00, 1),
        (body_id, 'Bikini Wax', 'Basic bikini line', 30, 45.00, 40.00, 2),
        (body_id, 'Brazilian Wax', 'Complete intimate area', 45, 75.00, 68.00, 3),
        (body_id, 'Full Leg Wax', 'Complete leg waxing', 45, 75.00, 68.00, 4),
        (body_id, 'Body Scrub', 'Full-body exfoliation', 60, 115.00, 105.00, 5);

    -- Makeup & Lashes
    INSERT INTO services (category_id, name, description, duration_minutes, base_price, member_price, display_order) VALUES
        (makeup_id, 'Special Event Makeup', 'Professional makeup application', 60, 85.00, 75.00, 1),
        (makeup_id, 'Bridal Makeup', 'Wedding day perfection', 90, 150.00, 135.00, 2),
        (makeup_id, 'Lash Extensions - Full Set', 'Individual lash application', 120, 195.00, 175.00, 3),
        (makeup_id, 'Lash Extensions - Fill', 'Maintenance for existing extensions', 60, 75.00, 68.00, 4),
        (makeup_id, 'Lash Lift', 'Natural lash enhancement', 60, 85.00, 75.00, 5);
END $$;

-- ================================================================
-- STAFF MEMBERS
-- ================================================================

INSERT INTO staff (first_name, last_name, email, phone, role, hire_date, hourly_rate, commission_rate, color_code, is_active) VALUES
    ('Sarah', 'Johnson', 'sarah.j@spa.com', '555-0101', 'stylist', '2022-03-15', 18.00, 45.00, '#FF6B6B', true),
    ('Michael', 'Chen', 'michael.c@spa.com', '555-0102', 'stylist', '2021-06-20', 22.00, 50.00, '#4ECDC4', true),
    ('Jessica', 'Martinez', 'jessica.m@spa.com', '555-0103', 'massage_therapist', '2023-01-10', 20.00, 40.00, '#95E1D3', true),
    ('David', 'Thompson', 'david.t@spa.com', '555-0104', 'massage_therapist', '2022-08-05', 19.00, 40.00, '#F38181', true),
    ('Emily', 'Rodriguez', 'emily.r@spa.com', '555-0105', 'esthetician', '2021-11-12', 21.00, 45.00, '#AA96DA', true),
    ('Amanda', 'Lee', 'amanda.l@spa.com', '555-0106', 'nail_tech', '2023-02-28', 17.00, 35.00, '#FCBAD3', true),
    ('Robert', 'Davis', 'robert.d@spa.com', '555-0108', 'manager', '2020-01-01', 28.00, 0.00, '#FFD93D', true)
ON CONFLICT (email) DO NOTHING;

-- ================================================================
-- STAFF AVAILABILITY (with proper TIME casting)
-- ================================================================

-- Sarah Johnson (Stylist) - Mon-Fri 9-6
INSERT INTO staff_availability (staff_id, day_of_week, start_time, end_time, break_start, break_end)
SELECT id, 1, '09:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'sarah.j@spa.com'
UNION ALL
SELECT id, 2, '09:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'sarah.j@spa.com'
UNION ALL
SELECT id, 3, '09:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'sarah.j@spa.com'
UNION ALL
SELECT id, 4, '09:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'sarah.j@spa.com'
UNION ALL
SELECT id, 5, '09:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'sarah.j@spa.com';

-- Michael Chen (Stylist) - Tue-Sat 10-7
INSERT INTO staff_availability (staff_id, day_of_week, start_time, end_time, break_start, break_end)
SELECT id, 2, '10:00'::TIME, '19:00'::TIME, '14:00'::TIME, '15:00'::TIME FROM staff WHERE email = 'michael.c@spa.com'
UNION ALL
SELECT id, 3, '10:00'::TIME, '19:00'::TIME, '14:00'::TIME, '15:00'::TIME FROM staff WHERE email = 'michael.c@spa.com'
UNION ALL
SELECT id, 4, '10:00'::TIME, '19:00'::TIME, '14:00'::TIME, '15:00'::TIME FROM staff WHERE email = 'michael.c@spa.com'
UNION ALL
SELECT id, 5, '10:00'::TIME, '19:00'::TIME, '14:00'::TIME, '15:00'::TIME FROM staff WHERE email = 'michael.c@spa.com'
UNION ALL
SELECT id, 6, '10:00'::TIME, '19:00'::TIME, '14:00'::TIME, '15:00'::TIME FROM staff WHERE email = 'michael.c@spa.com';

-- Jessica Martinez (Massage) - Mon-Fri 9-5
INSERT INTO staff_availability (staff_id, day_of_week, start_time, end_time, break_start, break_end)
SELECT id, 1, '09:00'::TIME, '17:00'::TIME, '12:00'::TIME, '13:00'::TIME FROM staff WHERE email = 'jessica.m@spa.com'
UNION ALL
SELECT id, 2, '09:00'::TIME, '17:00'::TIME, '12:00'::TIME, '13:00'::TIME FROM staff WHERE email = 'jessica.m@spa.com'
UNION ALL
SELECT id, 3, '09:00'::TIME, '17:00'::TIME, '12:00'::TIME, '13:00'::TIME FROM staff WHERE email = 'jessica.m@spa.com'
UNION ALL
SELECT id, 4, '09:00'::TIME, '17:00'::TIME, '12:00'::TIME, '13:00'::TIME FROM staff WHERE email = 'jessica.m@spa.com'
UNION ALL
SELECT id, 5, '09:00'::TIME, '17:00'::TIME, '12:00'::TIME, '13:00'::TIME FROM staff WHERE email = 'jessica.m@spa.com';

-- David Thompson (Massage) - Wed-Sun 11-7
INSERT INTO staff_availability (staff_id, day_of_week, start_time, end_time, break_start, break_end)
SELECT id, 0, '11:00'::TIME, '19:00'::TIME, '15:00'::TIME, '16:00'::TIME FROM staff WHERE email = 'david.t@spa.com'
UNION ALL
SELECT id, 3, '11:00'::TIME, '19:00'::TIME, '15:00'::TIME, '16:00'::TIME FROM staff WHERE email = 'david.t@spa.com'
UNION ALL
SELECT id, 4, '11:00'::TIME, '19:00'::TIME, '15:00'::TIME, '16:00'::TIME FROM staff WHERE email = 'david.t@spa.com'
UNION ALL
SELECT id, 5, '11:00'::TIME, '19:00'::TIME, '15:00'::TIME, '16:00'::TIME FROM staff WHERE email = 'david.t@spa.com'
UNION ALL
SELECT id, 6, '11:00'::TIME, '19:00'::TIME, '15:00'::TIME, '16:00'::TIME FROM staff WHERE email = 'david.t@spa.com';

-- Emily Rodriguez (Esthetician) - Mon-Fri 9-6
INSERT INTO staff_availability (staff_id, day_of_week, start_time, end_time, break_start, break_end)
SELECT id, 1, '09:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'emily.r@spa.com'
UNION ALL
SELECT id, 2, '09:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'emily.r@spa.com'
UNION ALL
SELECT id, 3, '09:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'emily.r@spa.com'
UNION ALL
SELECT id, 4, '09:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'emily.r@spa.com'
UNION ALL
SELECT id, 5, '09:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'emily.r@spa.com';

-- Amanda Lee (Nail Tech) - Tue-Sat 10-6
INSERT INTO staff_availability (staff_id, day_of_week, start_time, end_time, break_start, break_end)
SELECT id, 2, '10:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'amanda.l@spa.com'
UNION ALL
SELECT id, 3, '10:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'amanda.l@spa.com'
UNION ALL
SELECT id, 4, '10:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'amanda.l@spa.com'
UNION ALL
SELECT id, 5, '10:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'amanda.l@spa.com'
UNION ALL
SELECT id, 6, '10:00'::TIME, '18:00'::TIME, '13:00'::TIME, '14:00'::TIME FROM staff WHERE email = 'amanda.l@spa.com';

-- ================================================================
-- RETAIL PRODUCTS
-- ================================================================

INSERT INTO retail_products (sku, name, category, brand, retail_price, cost_price, current_stock, reorder_point, is_active) VALUES
    ('HC001', 'Professional Shampoo - Moisturizing 10oz', 'haircare', 'Salon Pro', 28.00, 14.00, 45, 10, true),
    ('HC002', 'Professional Conditioner - Moisturizing 10oz', 'haircare', 'Salon Pro', 28.00, 14.00, 42, 10, true),
    ('HC003', 'Color-Safe Shampoo 12oz', 'haircare', 'ColorGuard', 32.00, 16.00, 38, 10, true),
    ('HC004', 'Deep Conditioning Mask 8oz', 'haircare', 'Salon Pro', 45.00, 22.50, 25, 8, true),
    ('HC005', 'Anti-Frizz Serum 3oz', 'haircare', 'SmoothLux', 38.00, 19.00, 28, 8, true),
    ('SC001', 'Hydrating Face Cleanser 6oz', 'skincare', 'PureGlow', 35.00, 17.50, 40, 12, true),
    ('SC002', 'Anti-Aging Night Cream 2oz', 'skincare', 'AgeLess', 68.00, 34.00, 22, 8, true),
    ('SC003', 'Vitamin C Serum 1oz', 'skincare', 'PureGlow', 55.00, 27.50, 18, 6, true),
    ('SC004', 'Daily SPF 50 Moisturizer 3oz', 'skincare', 'SunShield', 42.00, 21.00, 35, 10, true),
    ('SC005', 'Hydrating Face Mask - Sheet Pack', 'skincare', 'PureGlow', 8.00, 4.00, 100, 25, true),
    ('BC001', 'Luxury Body Lotion 8oz', 'bodycare', 'SilkTouch', 36.00, 18.00, 32, 10, true),
    ('BC002', 'Aromatic Body Scrub 10oz', 'bodycare', 'SpaEssence', 44.00, 22.00, 20, 8, true),
    ('BC003', 'Essential Oil - Lavender 2oz', 'bodycare', 'AromaTherapy', 24.00, 12.00, 25, 8, true),
    ('NC001', 'Cuticle Oil Pen', 'nailcare', 'NailPro', 12.00, 6.00, 50, 15, true),
    ('NC002', 'Professional Nail File Set', 'nailcare', 'NailPro', 18.00, 9.00, 40, 12, true),
    ('NC003', 'Hand Cream - Intensive 3oz', 'nailcare', 'SilkTouch', 22.00, 11.00, 35, 10, true)
ON CONFLICT (sku) DO NOTHING;

-- ================================================================
-- SAMPLE CUSTOMERS
-- ================================================================

INSERT INTO customers (name, email, phone, date_of_birth, gender, first_visit, last_visit, total_visits, total_spent, loyalty_points, preferred_services, communication_preference) VALUES
    ('Emma Wilson', 'emma.w@email.com', '555-1001', '1985-03-15', 'Female', CURRENT_DATE - INTERVAL '180 days', CURRENT_DATE - INTERVAL '25 days', 8, 950.00, 950, ARRAY['Women''s Haircut', 'Classic Facial'], 'email'),
    ('James Brown', 'james.b@email.com', '555-1002', '1990-07-22', 'Male', CURRENT_DATE - INTERVAL '90 days', CURRENT_DATE - INTERVAL '30 days', 4, 320.00, 320, ARRAY['Men''s Haircut', 'Swedish Massage - 60 min'], 'sms'),
    ('Sophia Garcia', 'sophia.g@email.com', '555-1003', '1988-11-10', 'Female', CURRENT_DATE - INTERVAL '200 days', CURRENT_DATE - INTERVAL '60 days', 12, 1840.00, 1840, ARRAY['Balayage', 'Spa Pedicure'], 'email'),
    ('Michael Lee', 'michael.l@email.com', '555-1004', '1992-05-18', 'Male', CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE - INTERVAL '15 days', 3, 285.00, 285, ARRAY['Deep Tissue Massage - 60 min'], 'email'),
    ('Olivia Martinez', 'olivia.m@email.com', '555-1005', '1995-09-25', 'Female', CURRENT_DATE - INTERVAL '150 days', CURRENT_DATE - INTERVAL '35 days', 6, 780.00, 780, ARRAY['Gel Manicure', 'Anti-Aging Facial'], 'sms'),
    ('Ethan Davis', 'ethan.d@email.com', '555-1006', '1987-12-03', 'Male', CURRENT_DATE - INTERVAL '45 days', CURRENT_DATE - INTERVAL '10 days', 2, 190.00, 190, ARRAY['Men''s Haircut'], 'email'),
    ('Ava Rodriguez', 'ava.r@email.com', '555-1007', '1991-04-28', 'Female', CURRENT_DATE - INTERVAL '120 days', CURRENT_DATE - INTERVAL '75 days', 5, 685.00, 685, ARRAY['Women''s Haircut', 'Lash Extensions - Full Set'], 'email'),
    ('Noah Johnson', 'noah.j@email.com', '555-1008', '1989-08-14', 'Male', CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '5 days', 1, 95.00, 95, ARRAY['Swedish Massage - 60 min'], 'sms'),
    ('Isabella White', 'isabella.w@email.com', '555-1009', '1993-02-19', 'Female', CURRENT_DATE - INTERVAL '240 days', CURRENT_DATE - INTERVAL '20 days', 15, 2250.00, 2250, ARRAY['Full Highlights', 'Microdermabrasion', 'Spa Pedicure'], 'email'),
    ('Liam Taylor', 'liam.t@email.com', '555-1010', '1986-06-07', 'Male', CURRENT_DATE - INTERVAL '90 days', CURRENT_DATE - INTERVAL '50 days', 4, 420.00, 420, ARRAY['Men''s Haircut', 'Hot Stone Massage'], 'email')
ON CONFLICT (email) DO NOTHING;

-- ================================================================
-- SUCCESS MESSAGE
-- ================================================================

DO $$
BEGIN
    RAISE NOTICE '================================================================';
    RAISE NOTICE 'SEED DATA LOADED SUCCESSFULLY!';
    RAISE NOTICE '================================================================';
    RAISE NOTICE 'Data Loaded:';
    RAISE NOTICE '  ✓ 6 Service Categories';
    RAISE NOTICE '  ✓ 30 Professional Services';
    RAISE NOTICE '  ✓ 7 Staff Members';
    RAISE NOTICE '  ✓ Staff Availability Schedules';
    RAISE NOTICE '  ✓ 16 Retail Products';
    RAISE NOTICE '  ✓ 10 Sample Customers';
    RAISE NOTICE '';
    RAISE NOTICE 'Next: Deploy API to Fly.io! 🚀';
    RAISE NOTICE '================================================================';
END $$;