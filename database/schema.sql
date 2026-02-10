-- ================================================================
-- SPA/SALON MANAGEMENT SYSTEM - Supabase Schema
-- ================================================================
-- Optimized for Supabase with RLS policies and Edge Functions
-- Deploy: Copy-paste into Supabase SQL Editor

-- ================================================================
-- ENABLE EXTENSIONS
-- ================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search

-- ================================================================
-- CORE BUSINESS TABLES
-- ================================================================

-- Customers
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_number VARCHAR(20) UNIQUE NOT NULL DEFAULT 'CUST-' || LPAD(nextval('customers_seq')::TEXT, 6, '0'),
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

CREATE SEQUENCE IF NOT EXISTS customers_seq START 1;

-- Service Categories
CREATE TABLE IF NOT EXISTS service_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Services
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES service_categories(id) ON DELETE SET NULL,
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
CREATE TABLE IF NOT EXISTS staff (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_number VARCHAR(20) UNIQUE NOT NULL DEFAULT 'EMP-' || LPAD(nextval('staff_seq')::TEXT, 4, '0'),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    hourly_rate DECIMAL(10,2),
    commission_rate DECIMAL(5,2),
    is_active BOOLEAN DEFAULT true,
    color_code VARCHAR(7) DEFAULT '#3B82F6',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE SEQUENCE IF NOT EXISTS staff_seq START 1;

-- Staff Service Assignments
CREATE TABLE IF NOT EXISTS staff_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    staff_id UUID REFERENCES staff(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    proficiency_level VARCHAR(20) DEFAULT 'expert',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(staff_id, service_id)
);

-- Staff Availability
CREATE TABLE IF NOT EXISTS staff_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    staff_id UUID REFERENCES staff(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT true,
    break_start TIME,
    break_end TIME,
    effective_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Appointments
CREATE TABLE IF NOT EXISTS appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_number VARCHAR(20) UNIQUE NOT NULL DEFAULT 'APPT-' || LPAD(nextval('appointments_seq')::TEXT, 6, '0'),
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    staff_id UUID REFERENCES staff(id) ON DELETE SET NULL,
    scheduled_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'confirmed', 'checked-in', 'in-progress', 'completed', 'cancelled', 'no-show')),
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

CREATE SEQUENCE IF NOT EXISTS appointments_seq START 1;

-- Appointment Services
CREATE TABLE IF NOT EXISTS appointment_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_id UUID REFERENCES appointments(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id),
    staff_id UUID REFERENCES staff(id),
    start_time TIME,
    duration_minutes INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    final_price DECIMAL(10,2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Retail Products
CREATE TABLE IF NOT EXISTS retail_products (
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
CREATE TABLE IF NOT EXISTS sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sale_number VARCHAR(20) UNIQUE NOT NULL DEFAULT 'SALE-' || LPAD(nextval('sales_seq')::TEXT, 6, '0'),
    appointment_id UUID REFERENCES appointments(id),
    customer_id UUID REFERENCES customers(id),
    staff_id UUID REFERENCES staff(id),
    sale_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sale_type VARCHAR(20) NOT NULL CHECK (sale_type IN ('service', 'retail', 'package', 'gift-card')),
    subtotal DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    tip_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'paid' CHECK (payment_status IN ('pending', 'paid', 'refunded', 'partial')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE SEQUENCE IF NOT EXISTS sales_seq START 1;

-- Sale Line Items
CREATE TABLE IF NOT EXISTS sales_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sale_id UUID REFERENCES sales(id) ON DELETE CASCADE,
    item_type VARCHAR(20) NOT NULL CHECK (item_type IN ('service', 'product', 'package', 'gift-card')),
    service_id UUID REFERENCES services(id),
    product_id UUID REFERENCES retail_products(id),
    staff_id UUID REFERENCES staff(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_price DECIMAL(10,2) NOT NULL,
    commission_amount DECIMAL(10,2) DEFAULT 0,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inventory Transactions
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES retail_products(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('purchase', 'sale', 'adjustment', 'return', 'waste')),
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(10,2),
    reference_type VARCHAR(20),
    reference_id UUID,
    notes TEXT,
    transaction_date TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES staff(id)
);

-- AI Agent Tables
CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(50) NOT NULL,
    memory_type VARCHAR(20) NOT NULL CHECK (memory_type IN ('episodic', 'semantic', 'procedural')),
    content JSONB NOT NULL,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(50) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    reasoning TEXT NOT NULL,
    outcome JSONB,
    confidence DECIMAL(3,2),
    execution_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_agent VARCHAR(50) NOT NULL,
    to_agent VARCHAR(50) NOT NULL,
    topic VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('sent', 'delivered', 'processed')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- INDEXES
-- ================================================================

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_last_visit ON customers(last_visit);
CREATE INDEX IF NOT EXISTS idx_appointments_customer ON appointments(customer_id);
CREATE INDEX IF NOT EXISTS idx_appointments_staff ON appointments(staff_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON retail_products(category);
CREATE INDEX IF NOT EXISTS idx_agent_actions_date ON agent_actions(created_at);

-- ================================================================
-- FUNCTIONS & TRIGGERS
-- ================================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_services_updated_at BEFORE UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_staff_updated_at BEFORE UPDATE ON staff
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_appointments_updated_at BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_products_updated_at BEFORE UPDATE ON retail_products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

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
            loyalty_points = loyalty_points + FLOOR(NEW.total_amount)::INTEGER
        WHERE id = NEW.customer_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_customer_totals
AFTER INSERT OR UPDATE ON appointments
FOR EACH ROW EXECUTE FUNCTION update_customer_totals();

-- Update product stock on sale
CREATE OR REPLACE FUNCTION update_product_stock()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.item_type = 'product' AND NEW.product_id IS NOT NULL THEN
        UPDATE retail_products 
        SET current_stock = current_stock - NEW.quantity
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
FOR EACH ROW EXECUTE FUNCTION update_product_stock();

-- ================================================================
-- VIEWS FOR REPORTING
-- ================================================================

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

CREATE OR REPLACE VIEW vw_staff_performance AS
SELECT 
    s.id as staff_id,
    s.first_name || ' ' || s.last_name as staff_name,
    s.role,
    COUNT(DISTINCT a.id) as appointments_completed,
    SUM(a.total_amount) as service_revenue,
    COUNT(DISTINCT sa.id) as retail_transactions,
    SUM(CASE WHEN si.item_type = 'product' THEN si.total_price ELSE 0 END) as retail_revenue,
    SUM(si.commission_amount) as total_commission
FROM staff s
LEFT JOIN appointments a ON s.id = a.staff_id AND a.status = 'completed'
LEFT JOIN sales sa ON s.id = sa.staff_id
LEFT JOIN sales_items si ON sa.id = si.sale_id
WHERE s.is_active = true
GROUP BY s.id, s.first_name, s.last_name, s.role;

CREATE OR REPLACE VIEW vw_service_performance AS
SELECT 
    sc.name as category,
    s.name as service_name,
    s.duration_minutes,
    s.base_price,
    COUNT(aps.id) as times_booked,
    SUM(aps.final_price) as total_revenue,
    AVG(aps.final_price) as avg_price
FROM services s
JOIN service_categories sc ON s.category_id = sc.id
LEFT JOIN appointment_services aps ON s.id = aps.service_id
WHERE s.is_active = true
GROUP BY sc.name, s.name, s.duration_minutes, s.base_price
ORDER BY total_revenue DESC;

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
-- ROW LEVEL SECURITY (RLS)
-- ================================================================
-- Note: Enable RLS in Supabase dashboard if needed for multi-tenancy
-- For demo purposes, we'll keep it simple with public access

-- ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sales ENABLE ROW LEVEL SECURITY;

-- Example policy (commented out for demo):
-- CREATE POLICY "Public read access" ON customers FOR SELECT USING (true);
-- CREATE POLICY "Authenticated write access" ON customers FOR INSERT WITH CHECK (auth.role() = 'authenticated');
