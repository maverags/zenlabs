-- ================================================================
-- SPA/SALON MANAGEMENT SYSTEM - SUPABASE SCHEMA
-- ================================================================
-- Cloud-optimized for Supabase PostgreSQL
-- Includes Row Level Security (RLS) policies
-- ================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ================================================================
-- CORE BUSINESS TABLES
-- ================================================================

-- Customers
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_number VARCHAR(20) UNIQUE NOT NULL DEFAULT 'CUST' || LPAD(nextval('customer_seq')::TEXT, 6, '0'),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    first_visit DATE NOT NULL DEFAULT CURRENT_DATE,
    last_visit DATE,
    total_visits INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0,
    loyalty_points INTEGER DEFAULT 0,
    preferred_services TEXT[],
    communication_preference VARCHAR(20) DEFAULT 'email',
    marketing_consent BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE SEQUENCE customer_seq START 1;

-- Service Categories
CREATE TABLE service_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Services
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES service_categories(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    duration_minutes INTEGER NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    member_price DECIMAL(10,2),
    is_active BOOLEAN DEFAULT true,
    requires_deposit BOOLEAN DEFAULT false,
    deposit_amount DECIMAL(10,2),
    cancellation_hours INTEGER DEFAULT 24,
    max_advance_booking_days INTEGER DEFAULT 90,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Staff Members
CREATE TABLE staff (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_number VARCHAR(20) UNIQUE NOT NULL DEFAULT 'EMP' || LPAD(nextval('staff_seq')::TEXT, 4, '0'),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    hourly_rate DECIMAL(10,2),
    commission_rate DECIMAL(5,2),
    is_active BOOLEAN DEFAULT true,
    color_code VARCHAR(7),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE SEQUENCE staff_seq START 1;

-- Staff Service Assignments
CREATE TABLE staff_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    staff_id UUID REFERENCES staff(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    proficiency_level VARCHAR(20) DEFAULT 'expert',
    UNIQUE(staff_id, service_id)
);

-- Staff Availability
CREATE TABLE staff_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    staff_id UUID REFERENCES staff(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT true,
    break_start TIME,
    break_end TIME,
    effective_date DATE,
    notes TEXT
);

-- Appointments
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_number VARCHAR(20) UNIQUE NOT NULL DEFAULT 'APT' || LPAD(nextval('appointment_seq')::TEXT, 6, '0'),
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    staff_id UUID REFERENCES staff(id) ON DELETE SET NULL,
    scheduled_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    total_duration INTEGER NOT NULL,
    subtotal DECIMAL(10,2) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) DEFAULT 0,
    deposit_paid DECIMAL(10,2) DEFAULT 0,
    booking_source VARCHAR(50) DEFAULT 'walk-in',
    reminder_sent BOOLEAN DEFAULT false,
    confirmation_sent BOOLEAN DEFAULT false,
    customer_notes TEXT,
    staff_notes TEXT,
    cancellation_reason TEXT,
    cancelled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE SEQUENCE appointment_seq START 1;

-- Appointment Services
CREATE TABLE appointment_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_id UUID REFERENCES appointments(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id),
    staff_id UUID REFERENCES staff(id),
    start_time TIME,
    duration_minutes INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    final_price DECIMAL(10,2) NOT NULL,
    notes TEXT
);

-- ================================================================
-- RETAIL & POS
-- ================================================================

-- Retail Products
CREATE TABLE retail_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    brand VARCHAR(100),
    description TEXT,
    retail_price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    current_stock INTEGER DEFAULT 0,
    minimum_stock INTEGER DEFAULT 0,
    maximum_stock INTEGER DEFAULT 100,
    reorder_point INTEGER DEFAULT 10,
    supplier VARCHAR(100),
    barcode VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    track_inventory BOOLEAN DEFAULT true,
    taxable BOOLEAN DEFAULT true,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sales Transactions
CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sale_number VARCHAR(20) UNIQUE NOT NULL DEFAULT 'SALE' || LPAD(nextval('sale_seq')::TEXT, 6, '0'),
    appointment_id UUID REFERENCES appointments(id),
    customer_id UUID REFERENCES customers(id),
    staff_id UUID REFERENCES staff(id),
    sale_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sale_type VARCHAR(20) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    tip_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'paid',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE SEQUENCE sale_seq START 1;

-- Sale Line Items
CREATE TABLE sales_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sale_id UUID REFERENCES sales(id) ON DELETE CASCADE,
    item_type VARCHAR(20) NOT NULL,
    service_id UUID REFERENCES services(id),
    product_id UUID REFERENCES retail_products(id),
    staff_id UUID REFERENCES staff(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_price DECIMAL(10,2) NOT NULL,
    commission_amount DECIMAL(10,2) DEFAULT 0,
    description TEXT
);

-- Inventory Transactions
CREATE TABLE inventory_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES retail_products(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(10,2),
    reference_type VARCHAR(20),
    reference_id UUID,
    notes TEXT,
    transaction_date TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES staff(id)
);

-- ================================================================
-- AI AGENT SYSTEM TABLES
-- ================================================================

CREATE TABLE agent_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(50) NOT NULL,
    memory_type VARCHAR(20) NOT NULL,
    content JSONB NOT NULL,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE agent_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(50) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    reasoning TEXT NOT NULL,
    outcome JSONB,
    confidence DECIMAL(3,2),
    execution_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE agent_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_agent VARCHAR(50) NOT NULL,
    to_agent VARCHAR(50) NOT NULL,
    topic VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'sent',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- INDEXES
-- ================================================================

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_last_visit ON customers(last_visit);
CREATE INDEX idx_appointments_customer ON appointments(customer_id);
CREATE INDEX idx_appointments_staff ON appointments(staff_id);
CREATE INDEX idx_appointments_date ON appointments(scheduled_date);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_sales_staff ON sales(staff_id);
CREATE INDEX idx_products_sku ON retail_products(sku);
CREATE INDEX idx_products_category ON retail_products(category);
CREATE INDEX idx_inventory_product ON inventory_transactions(product_id);
CREATE INDEX idx_agent_memory_agent ON agent_memory(agent_id);
CREATE INDEX idx_agent_actions_agent ON agent_actions(agent_id);
CREATE INDEX idx_agent_actions_date ON agent_actions(created_at);

-- ================================================================
-- FUNCTIONS & TRIGGERS
-- ================================================================

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_staff_updated_at BEFORE UPDATE ON staff
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_retail_products_updated_at BEFORE UPDATE ON retail_products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update customer totals on appointment completion
CREATE OR REPLACE FUNCTION update_customer_totals()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND (OLD.status IS NULL OR OLD.status != 'completed') THEN
        UPDATE customers 
        SET 
            last_visit = NEW.scheduled_date,
            total_visits = total_visits + 1,
            total_spent = total_spent + NEW.total_amount,
            loyalty_points = loyalty_points + FLOOR(NEW.total_amount)::INTEGER,
            updated_at = NOW()
        WHERE id = NEW.customer_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_customer_totals
AFTER UPDATE ON appointments
FOR EACH ROW
EXECUTE FUNCTION update_customer_totals();

-- Update product stock on sale
CREATE OR REPLACE FUNCTION update_product_stock()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.item_type = 'product' AND NEW.product_id IS NOT NULL THEN
        UPDATE retail_products 
        SET 
            current_stock = current_stock - NEW.quantity,
            updated_at = NOW()
        WHERE id = NEW.product_id;
        
        INSERT INTO inventory_transactions 
            (product_id, transaction_type, quantity, reference_type, reference_id, transaction_date)
        VALUES 
            (NEW.product_id, 'sale', -NEW.quantity, 'sale', NEW.sale_id, NOW());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_product_stock
AFTER INSERT ON sales_items
FOR EACH ROW
EXECUTE FUNCTION update_product_stock();

-- ================================================================
-- REPORTING VIEWS
-- ================================================================

-- Daily Sales Summary
CREATE OR REPLACE VIEW vw_daily_sales AS
SELECT 
    DATE(sale_date) as sale_date,
    COUNT(*) as transaction_count,
    SUM(subtotal) as subtotal,
    SUM(discount_amount) as total_discounts,
    SUM(tax_amount) as total_tax,
    SUM(tip_amount) as total_tips,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_ticket_size
FROM sales
GROUP BY DATE(sale_date)
ORDER BY sale_date DESC;

-- Staff Performance
CREATE OR REPLACE VIEW vw_staff_performance AS
SELECT 
    s.id as staff_id,
    s.first_name || ' ' || s.last_name as staff_name,
    s.role,
    COUNT(DISTINCT a.id) as appointments_completed,
    COALESCE(SUM(a.total_amount), 0) as service_revenue,
    COUNT(DISTINCT sa.id) as retail_transactions,
    COALESCE(SUM(CASE WHEN si.item_type = 'product' THEN si.total_price ELSE 0 END), 0) as retail_revenue,
    COALESCE(SUM(si.commission_amount), 0) as total_commission
FROM staff s
LEFT JOIN appointments a ON s.id = a.staff_id AND a.status = 'completed'
LEFT JOIN sales sa ON s.id = sa.staff_id
LEFT JOIN sales_items si ON sa.id = si.sale_id
WHERE s.is_active = true
GROUP BY s.id, s.first_name, s.last_name, s.role;

-- Service Performance
CREATE OR REPLACE VIEW vw_service_performance AS
SELECT 
    sc.name as category,
    s.name as service_name,
    s.duration_minutes,
    s.base_price,
    COUNT(aps.id) as times_booked,
    COALESCE(SUM(aps.final_price), 0) as total_revenue,
    COALESCE(AVG(aps.final_price), 0) as avg_price
FROM services s
JOIN service_categories sc ON s.category_id = sc.id
LEFT JOIN appointment_services aps ON s.id = aps.service_id
WHERE s.is_active = true
GROUP BY sc.name, s.name, s.duration_minutes, s.base_price
ORDER BY total_revenue DESC;

-- Low Stock Products
CREATE OR REPLACE VIEW vw_low_stock_products AS
SELECT 
    sku,
    name,
    category,
    current_stock,
    reorder_point,
    minimum_stock,
    (reorder_point - current_stock) as units_needed
FROM retail_products
WHERE current_stock <= reorder_point
  AND is_active = true
ORDER BY (reorder_point - current_stock) DESC;

-- ================================================================
-- ROW LEVEL SECURITY (RLS) - Enable for production
-- ================================================================
-- Uncomment these when ready to add authentication

-- ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE staff ENABLE ROW LEVEL SECURITY;

-- Example policy (create policies based on your auth setup):
-- CREATE POLICY "Users can view their own data"
--   ON customers FOR SELECT
--   USING (auth.uid()::text = user_id::text);

-- ================================================================
-- API FUNCTIONS (Exposed via Supabase PostgREST)
-- ================================================================

-- Get available time slots for booking
CREATE OR REPLACE FUNCTION get_available_slots(
    p_staff_id UUID,
    p_date DATE,
    p_duration INTEGER
)
RETURNS TABLE(start_time TIME, end_time TIME) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.slot_time as start_time,
        (t.slot_time + (p_duration || ' minutes')::INTERVAL)::TIME as end_time
    FROM generate_series(
        '09:00'::TIME,
        '18:00'::TIME,
        '15 minutes'::INTERVAL
    ) t(slot_time)
    WHERE NOT EXISTS (
        SELECT 1 FROM appointments a
        WHERE a.staff_id = p_staff_id
          AND a.scheduled_date = p_date
          AND a.status NOT IN ('cancelled', 'no-show')
          AND t.slot_time >= a.start_time
          AND t.slot_time < a.end_time
    )
    AND t.slot_time + (p_duration || ' minutes')::INTERVAL <= '19:00'::TIME;
END;
$$ LANGUAGE plpgsql;

-- Get dashboard metrics
CREATE OR REPLACE FUNCTION get_dashboard_metrics(p_date DATE DEFAULT CURRENT_DATE)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'today_appointments', (
            SELECT COUNT(*) FROM appointments 
            WHERE scheduled_date = p_date
        ),
        'today_revenue', (
            SELECT COALESCE(SUM(total_amount), 0) 
            FROM sales 
            WHERE DATE(sale_date) = p_date
        ),
        'active_staff', (
            SELECT COUNT(*) FROM staff WHERE is_active = true
        ),
        'low_stock_items', (
            SELECT COUNT(*) FROM vw_low_stock_products
        ),
        'at_risk_customers', (
            SELECT COUNT(*) FROM customers
            WHERE last_visit < CURRENT_DATE - INTERVAL '45 days'
              AND last_visit >= CURRENT_DATE - INTERVAL '120 days'
              AND total_visits > 2
        )
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;
