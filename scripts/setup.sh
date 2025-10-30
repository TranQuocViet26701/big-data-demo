#!/bin/bash

###############################################################################
# Big Data Demo - Complete Setup Script
# This script automates the entire demo setup process
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed: $(docker --version)"

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed: $(docker-compose --version)"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    print_success "Python 3 is installed: $(python3 --version)"
}

# Generate clickstream data
generate_data() {
    print_header "Step 1: Generating Clickstream Data"

    cd data
    if [ -f "clickstream_large.txt" ]; then
        print_info "Data file already exists. Skipping generation."
    else
        print_info "Generating 10,000 clickstream records..."
        python3 generate_clickstream.py 10000
        print_success "Data generated successfully!"
    fi
    cd ..
}

# Start Docker services
start_services() {
    print_header "Step 2: Starting Docker Services"

    print_info "Building and starting containers..."
    docker-compose up -d

    print_success "All services started!"

    print_info "Waiting for services to be healthy..."
    sleep 30
}

# Initialize HDFS
init_hdfs() {
    print_header "Step 3: Initializing HDFS"

    print_info "Running HDFS initialization script..."
    bash scripts/init-hdfs.sh

    print_success "HDFS initialized!"
}

# Initialize HBase
init_hbase() {
    print_header "Step 4: Initializing HBase"

    print_info "Running HBase initialization script..."
    bash scripts/init-hbase.sh

    print_success "HBase initialized!"
}

# Display access information
show_info() {
    print_header "🎉 Setup Complete!"

    echo "You can now access the following services:"
    echo ""
    echo -e "${GREEN}📊 Streamlit Dashboard:${NC}"
    echo -e "   ${BLUE}http://localhost:8501${NC}"
    echo ""
    echo -e "${GREEN}🗄️  HDFS NameNode Web UI:${NC}"
    echo -e "   ${BLUE}http://localhost:9870${NC}"
    echo ""
    echo -e "${GREEN}⚡ Spark Master Web UI:${NC}"
    echo -e "   ${BLUE}http://localhost:8080${NC}"
    echo ""
    echo -e "${GREEN}🔧 HBase Master Web UI:${NC}"
    echo -e "   ${BLUE}http://localhost:16010${NC}"
    echo ""
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo "   1. Open the Streamlit Dashboard: http://localhost:8501"
    echo "   2. Run the Spark job: bash scripts/run-spark-job.sh"
    echo "   3. View the results in the dashboard"
    echo ""
    echo -e "${YELLOW}📖 Demo Workflow (from demo_script.md):${NC}"
    echo "   Bước 1 (HDFS): View data in HDFS Web UI (port 9870)"
    echo "   Bước 2 (Spark): Run Spark job to analyze data (port 8080)"
    echo "   Bước 3 (HBase): Query results instantly (via dashboard)"
    echo ""
    echo -e "${YELLOW}🛠️  Useful Commands:${NC}"
    echo "   - View logs:           docker-compose logs -f [service-name]"
    echo "   - Stop services:       docker-compose down"
    echo "   - Restart services:    docker-compose restart"
    echo "   - Run sample queries:  bash scripts/sample-queries.sh"
    echo ""
}

# Main execution
main() {
    print_header "🚀 Big Data Demo - Automated Setup"

    check_prerequisites
    generate_data
    start_services
    init_hdfs
    init_hbase
    show_info
}

# Run main function
main
