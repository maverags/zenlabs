-- ================================================================
-- SPA/SALON AGENTIC SYSTEM - SUPABASE SCHEMA
-- ================================================================
-- Optimized for Supabase with Row Level Security
-- Deploy via Supabase SQL Editor

-- ================================================================
-- CORE BUSINESS TABLES
-- ================================================================

-- Customers
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_number TEXT UNIQUE NOT NULL DEFAULT 'CUST-' || LPAD(nextval('customer_number_seq')::TEXT, 6, '0'),
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT NOT NULL,
    date_of_birth DATE,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    first_visit DATE NOT NULL DEFAULT CURRENT_DATE,
    last_visit DATE,
    total_visits INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0,
    loyalty_points INTEGER DEFAULT 0,
    preferred_services TEXT[],
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create sequence for customer numbers
CREATE SEQUENCE customer_number_seq START 1;

-- Service Categories
CREATE TABLE service_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT true
);

-- Services
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES service_categories(id),
    name TEXT NOT NULL,
    description TEXT,
    duration_minutes INTEGER NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    member_price DECIMAL(10,2),
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Staff
CREATE TABLE staff (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_number TEXT UNIQUE NOT NULL DEFAULT 'EMP-' || LPAD(nextval('employee_number_seq')::TEXT, 4, '0'),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    role TEXT NOT NULL,
    hire_date DATE NOT NULL,
    hourly_rate DECIMAL(10,2),
    commission_rate DECIMAL(5,2),
    is_active BOOLEAN DEFAULT true,
    color_code TEXT DEFAULT '#4ECDC4',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE SEQUENCE employee_number_seq START 1;

-- Staff Availability
CREATE TABLE staff_availability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staff_id UUID REFERENCES staff(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    break_start TIME,
    break_end TIME
);

-- Appointments
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_number TEXT UNIQUE NOT NULL DEFAULT 'APPT-' || LPAD(nextval('appointment_number_seq')::TEXT, 6, '0'),
    customer_id UUID REFERENCES customers(id),
    staff_id UUID REFERENCES staff(id),
    scheduled_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status TEXT NOT NULL DEFAULT 'scheduled',
    total_amount DECIMAL(10,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE SEQUENCE appointment_number_seq START 1;

-- Appointment Services
CREATE TABLE appointment_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id UUID REFERENCES appointments(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id),
    price DECIMAL(10,2) NOT NULL,
    duration_minutes INTEGER NOT NULL
);

-- Retail Products
CREATE TABLE retail_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    brand TEXT,
    retail_price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    current_stock INTEGER DEFAULT 0,
    reorder_point INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sales
CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sale_number TEXT UNIQUE NOT NULL DEFAULT 'SALE-' || LPAD(nextval('sale_number_seq')::TEXT, 6, '0'),
    appointment_id UUID REFERENCES appointments(id),
    customer_id UUID REFERENCES customers(id),
    staff_id UUID REFERENCES staff(id),
    sale_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    subtotal DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    tip_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method TEXT NOT NULL
);

CREATE SEQUENCE sale_number_seq START 1;

-- Sales Items
CREATE TABLE sales_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sale_id UUID REFERENCES sales(id) ON DELETE CASCADE,
    item_type TEXT NOT NULL,
    service_id UUID REFERENCES services(id),
    product_id UUID REFERENCES retail_products(id),
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL
);

-- ================================================================
-- AI AGENT TABLES
-- ================================================================

CREATE TABLE agent_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE agent_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    outcome JSONB,
    confidence DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- INDEXES
-- ================================================================

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_appointments_date ON appointments(scheduled_date);
CREATE INDEX idx_appointments_customer ON appointments(customer_id);
CREATE INDEX idx_appointments_staff ON appointments(staff_id);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_agent_actions_agent ON agent_actions(agent_id);

-- ================================================================
-- SAMPLE DATA - SERVICE CATEGORIES
-- ================================================================

INSERT INTO service_categories (name, description, display_order) VALUES
    ('Hair Services', 'Cuts, color, styling', 1),
    ('Spa & Massage', 'Relaxation and therapeutic massage', 2),
    ('Skincare & Facials', 'Professional facial treatments', 3),
    ('Nails', 'Manicures, pedicures, nail art', 4),
    ('Body Treatments', 'Waxing, body treatments', 5);

-- ================================================================
-- SAMPLE DATA - SERVICES
-- ================================================================

INSERT INTO services (category_id, name, description, duration_minutes, base_price, member_price) 
SELECT id, 'Women''s Haircut', 'Precision cut with style', 60, 75, 68 FROM service_categories WHERE name = 'Hair Services'
UNION ALL SELECT id, 'Men''s Haircut', 'Classic cut', 45, 45, 40 FROM service_categories WHERE name = 'Hair Services'
UNION ALL SELECT id, 'Balayage', 'Hand-painted color', 180, 225, 200 FROM service_categories WHERE name = 'Hair Services'
UNION ALL SELECT id, 'Swedish Massage - 60min', 'Relaxing massage', 60, 95, 85 FROM service_categories WHERE name = 'Spa & Massage'
UNION ALL SELECT id, 'Deep Tissue - 60min', 'Therapeutic relief', 60, 110, 100 FROM service_categories WHERE name = 'Spa & Massage'
UNION ALL SELECT id, 'Hot Stone Massage', 'Heated stone therapy', 90, 145, 130 FROM service_categories WHERE name = 'Spa & Massage'
UNION ALL SELECT id, 'Classic Facial', 'Deep cleanse and mask', 60, 95, 85 FROM service_categories WHERE name = 'Skincare & Facials'
UNION ALL SELECT id, 'Anti-Aging Facial', 'Peptide treatment', 75, 135, 120 FROM service_categories WHERE name = 'Skincare & Facials'
UNION ALL SELECT id, 'Gel Manicure', 'Long-lasting gel', 60, 55, 50 FROM service_categories WHERE name = 'Nails'
UNION ALL SELECT id, 'Spa Pedicure', 'Ultimate foot treatment', 90, 95, 85 FROM service_categories WHERE name = 'Nails';

-- ================================================================
-- SAMPLE DATA - STAFF
-- ================================================================

INSERT INTO staff (first_name, last_name, email, role, hire_date, commission_rate, color_code) VALUES
    ('Sarah', 'Johnson', 'sarah.j@spa.com', 'stylist', '2022-03-15', 45.00, '#FF6B6B'),
    ('Michael', 'Chen', 'michael.c@spa.com', 'stylist', '2021-06-20', 50.00, '#4ECDC4'),
    ('Jessica', 'Martinez', 'jessica.m@spa.com', 'massage_therapist', '2023-01-10', 40.00, '#95E1D3'),
    ('Emily', 'Rodriguez', 'emily.r@spa.com', 'esthetician', '2021-11-12', 45.00, '#AA96DA');

-- ================================================================
-- SAMPLE DATA - STAFF AVAILABILITY
-- ================================================================

-- Sarah (Stylist) - Mon-Fri 9-6
INSERT INTO staff_availability (staff_id, day_of_week, start_time, end_time, break_start, break_end)
SELECT id, 1, '09:00', '18:00', '13:00', '14:00' FROM staff WHERE email = 'sarah.j@spa.com'
UNION ALL SELECT id, 2, '09:00', '18:00', '13:00', '14:00' FROM staff WHERE email = 'sarah.j@spa.com'
UNION ALL SELECT id, 3, '09:00', '18:00', '13:00', '14:00' FROM staff WHERE email = 'sarah.j@spa.com'
UNION ALL SELECT id, 4, '09:00', '18:00', '13:00', '14:00' FROM staff WHERE email = 'sarah.j@spa.com'
UNION ALL SELECT id, 5, '09:00', '18:00', '13:00', '14:00' FROM staff WHERE email = 'sarah.j@spa.com';

-- Michael (Stylist) - Tue-Sat 10-7
INSERT INTO staff_availability (staff_id, day_of_week, start_time, end_time, break_start, break_end)
SELECT id, 2, '10:00', '19:00', '14:00', '15:00' FROM staff WHERE email = 'michael.c@spa.com'
UNION ALL SELECT id, 3, '10:00', '19:00', '14:00', '15:00' FROM staff WHERE email = 'michael.c@spa.com'
UNION ALL SELECT id, 4, '10:00', '19:00', '14:00', '15:00' FROM staff WHERE email = 'michael.c@spa.com'
UNION ALL SELECT id, 5, '10:00', '19:00', '14:00', '15:00' FROM staff WHERE email = 'michael.c@spa.com'
UNION ALL SELECT id, 6, '10:00', '19:00', '14:00', '15:00' FROM staff WHERE email = 'michael.c@spa.com';

-- Jessica (Therapist) - Mon-Fri 9-5
INSERT INTO staff_availability (staff_id, day_of_week, start_time, end_time, break_start, break_end)
SELECT id, 1, '09:00', '17:00', '12:00', '13:00' FROM staff WHERE email = 'jessica.m@spa.com'
UNION ALL SELECT id, 2, '09:00', '17:00', '12:00', '13:00' FROM staff WHERE email = 'jessica.m@spa.com'
UNION ALL SELECT id, 3, '09:00', '17:00', '12:00', '13:00' FROM staff WHERE email = 'jessica.m@spa.com'
UNION ALL SELECT id, 4, '09:00', '17:00', '12:00', '13:00' FROM staff WHERE email = 'jessica.m@spa.com'
UNION ALL SELECT id, 5, '09:00', '17:00', '12:00', '13:00' FROM staff WHERE email = 'jessica.m@spa.com';

-- Emily (Esthetician) - Mon-Fri 9-6
INSERT INTO staff_availability (staff_id, day_of_week, start_time, end_time, break_start, break_end)
SELECT id, 1, '09:00', '18:00', '13:00', '14:00' FROM staff WHERE email = 'emily.r@spa.com'
UNION ALL SELECT id, 2, '09:00', '18:00', '13:00', '14:00' FROM staff WHERE email = 'emily.r@spa.com'
UNION ALL SELECT id, 3, '09:00', '18:00', '13:00', '14:00' FROM staff WHERE email = 'emily.r@spa.com'
UNION ALL SELECT id, 4, '09:00', '18:00', '13:00', '14:00' FROM staff WHERE email = 'emily.r@spa.com'
UNION ALL SELECT id, 5, '09:00', '18:00', '13:00', '14:00' FROM staff WHERE email = 'emily.r@spa.com';

-- ================================================================
-- SAMPLE DATA - RETAIL PRODUCTS
-- ================================================================

INSERT INTO retail_products (sku, name, category, brand, retail_price, cost_price, current_stock) VALUES
    ('HC001', 'Professional Shampoo 10oz', 'haircare', 'Salon Pro', 28.00, 14.00, 45),
    ('HC002', 'Professional Conditioner 10oz', 'haircare', 'Salon Pro', 28.00, 14.00, 42),
    ('SC001', 'Hydrating Face Cleanser', 'skincare', 'PureGlow', 35.00, 17.50, 40),
    ('SC002', 'Anti-Aging Night Cream', 'skincare', 'AgeLess', 68.00, 34.00, 22),
    ('NC001', 'Cuticle Oil Pen', 'nailcare', 'NailPro', 12.00, 6.00, 50);

-- ================================================================
-- REPORTING VIEWS
-- ================================================================

CREATE OR REPLACE VIEW vw_daily_sales AS
SELECT 
    DATE(sale_date) as sale_date,
    COUNT(*) as transaction_count,
    SUM(subtotal) as subtotal,
    SUM(tax_amount) as tax,
    SUM(tip_amount) as tips,
    SUM(total_amount) as total_revenue
FROM sales
GROUP BY DATE(sale_date)
ORDER BY sale_date DESC;

CREATE OR REPLACE VIEW vw_staff_performance AS
SELECT 
    s.id,
    s.first_name || ' ' || s.last_name as staff_name,
    s.role,
    COUNT(DISTINCT a.id) as appointments,
    SUM(a.total_amount) as revenue
FROM staff s
LEFT JOIN appointments a ON s.id = a.staff_id AND a.status = 'completed'
GROUP BY s.id, s.first_name, s.last_name, s.role;

CREATE OR REPLACE VIEW vw_low_stock AS
SELECT sku, name, current_stock, reorder_point
FROM retail_products
WHERE current_stock <= reorder_point AND is_active = true;
