#!/bin/bash

# Restaurant Menu API Test Script
# Tests all API endpoints with comprehensive coverage

# Configuration
BASE_URL="http://localhost:8000"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_test() {
    echo -e "${YELLOW}Testing:${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    ((PASSED_TESTS++))
}

print_failure() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    ((FAILED_TESTS++))
}

run_test() {
    local description="$1"
    local url="$2"
    local expected_status="${3:-200}"

    print_test "$description"
    ((TOTAL_TESTS++))

    echo "Running: curl -s -w \"HTTPSTATUS:%{http_code}\" \"$url\""

    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url")
    http_status=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//g')

    if [ "$http_status" -eq "$expected_status" ]; then
        print_success "Status $http_status"
        if [ "$expected_status" -eq 200 ]; then
            echo "Response preview: $(echo "$body" | head -c 200)..."
        fi
    else
        print_failure "Expected status $expected_status, got $http_status"
        echo "Response: $body"
    fi
    echo
}


run_post_test() {
    local description="$1"
    local url="$2"
    local data="$3"
    local expected_status="${4:-200}"
    
    print_test "$description"
    ((TOTAL_TESTS++))
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$url")
    http_status=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//g')
    
    if [ "$http_status" -eq "$expected_status" ]; then
        print_success "Status $http_status"
        if [ "$expected_status" -eq 200 ]; then
            echo "Response preview: $(echo "$body" | head -c 200)..."
        fi
    else
        print_failure "Expected status $expected_status, got $http_status"
        echo "Response: $body"
    fi
    echo
}

# Check if server is running
print_header "Server Health Check"
print_test "Checking if API server is running at $BASE_URL"

if ! curl -s "$BASE_URL/docs" > /dev/null; then
    echo -e "${RED}ERROR: API server is not running at $BASE_URL${NC}"
    echo "Please start the server with: python cli.py serve"
    exit 1
fi

print_success "Server is running"

# Start testing
echo -e "\n${BLUE}Starting comprehensive API tests...${NC}\n"

# ===============================
# RESTAURANT ENDPOINTS
# ===============================
print_header "Restaurant Endpoints"

run_test "Get all restaurants" "$BASE_URL/restaurants"

# Get first restaurant name for subsequent tests
RESTAURANT_NAME=$(curl -s "$BASE_URL/restaurants" | jq -r '.[0]' 2>/dev/null || echo "TestRestaurant")

run_test "Get specific restaurant menu" "$BASE_URL/restaurants/$RESTAURANT_NAME"

run_test "Get restaurant sections" "$BASE_URL/restaurants/$RESTAURANT_NAME/sections"

# Get first section name for subsequent tests
SECTION_NAME=$(curl -s "$BASE_URL/restaurants/$RESTAURANT_NAME/sections" | jq -r '.[0]' 2>/dev/null || echo "TestSection")

run_test "Get section items" "$BASE_URL/restaurants/$RESTAURANT_NAME/sections/$SECTION_NAME"

run_test "Get all restaurant items" "$BASE_URL/restaurants/$RESTAURANT_NAME/items"

run_test "Get restaurant items with price filter (< 20)" "$BASE_URL/restaurants/$RESTAURANT_NAME/items?price_lt=20"

run_test "Get restaurant items with price filter (> 10)" "$BASE_URL/restaurants/$RESTAURANT_NAME/items?price_gt=10"

run_test "Get restaurant items with price range (10-30)" "$BASE_URL/restaurants/$RESTAURANT_NAME/items?price_gt=10&price_lt=30"

run_test "Get restaurant items sorted by price (asc)" "$BASE_URL/restaurants/$RESTAURANT_NAME/items?sort_by=price&order=asc"

run_test "Get restaurant items sorted by price (desc)" "$BASE_URL/restaurants/$RESTAURANT_NAME/items?sort_by=price&order=desc"

run_test "Get restaurant items sorted by name (asc)" "$BASE_URL/restaurants/$RESTAURANT_NAME/items?sort_by=name&order=asc"

run_test "Get restaurant items sorted by name (desc)" "$BASE_URL/restaurants/$RESTAURANT_NAME/items?sort_by=name&order=desc"

# Test error cases
run_test "Get non-existent restaurant (404)" "$BASE_URL/restaurants/NonExistentRestaurant" 404

run_test "Get non-existent section (404)" "$BASE_URL/restaurants/$RESTAURANT_NAME/sections/NonExistentSection" 404

# ===============================
# SEARCH ENDPOINTS
# ===============================
print_header "Cross-Restaurant Search Endpoints"

run_test "Search items without filters" "$BASE_URL/search/items"

run_test "Search items by query (chicken)" "$BASE_URL/search/items?query=chicken"

run_test "Search items by query (salad)" "$BASE_URL/search/items?query=salad"

run_test "Search items with price filter (< 15)" "$BASE_URL/search/items?price_lt=15"

run_test "Search items with price filter (> 20)" "$BASE_URL/search/items?price_gt=20"

run_test "Search items with price range (10-25)" "$BASE_URL/search/items?price_gt=10&price_lt=25"

run_test "Search items by restaurant filter" "$BASE_URL/search/items?restaurant=$RESTAURANT_NAME"

run_test "Search items with query and price filter" "$BASE_URL/search/items?query=pasta&price_lt=30"

run_test "Search items sorted by price (asc)" "$BASE_URL/search/items?sort_by=price&order=asc"

run_test "Search items sorted by price (desc)" "$BASE_URL/search/items?sort_by=price&order=desc"

run_test "Search items sorted by name" "$BASE_URL/search/items?sort_by=name&order=asc"

run_test "Search items with limit (10)" "$BASE_URL/search/items?limit=10"

run_test "Search items with limit (1)" "$BASE_URL/search/items?limit=1"

run_test "Search by price range (5-15)" "$BASE_URL/search/by-price-range?min_price=5&max_price=15"

run_test "Search by price range (10-20)" "$BASE_URL/search/by-price-range?min_price=10&max_price=20"

run_test "Search by price range (15-25)" "$BASE_URL/search/by-price-range?min_price=15&max_price=25"

run_test "Search by price range with limit (5)" "$BASE_URL/search/by-price-range?min_price=10&max_price=30&limit=5"

run_test "Find restaurants with item (salad)" "$BASE_URL/search/restaurants-with-item?item_name=salad"

run_test "Find restaurants with item (chicken)" "$BASE_URL/search/restaurants-with-item?item_name=chicken"

run_test "Find restaurants with item (pizza)" "$BASE_URL/search/restaurants-with-item?item_name=pizza"

run_test "Find restaurants with item (burger)" "$BASE_URL/search/restaurants-with-item?item_name=burger"

# Test error cases for search
run_test "Search by invalid price range (400)" "$BASE_URL/search/by-price-range?min_price=30&max_price=10" 400

run_test "Search by negative price range (422)" "$BASE_URL/search/by-price-range?min_price=-5&max_price=10" 422

run_test "Search with invalid limit (422)" "$BASE_URL/search/items?limit=1000" 422

# ===============================
# STATISTICS ENDPOINTS
# ===============================
print_header "Statistics Endpoints"

run_test "Get restaurant statistics" "$BASE_URL/stats/restaurant/$RESTAURANT_NAME"

# Test error case
run_test "Get statistics for non-existent restaurant (404)" "$BASE_URL/stats/restaurant/NonExistentRestaurant" 404

# ===============================
# API DOCUMENTATION ENDPOINTS
# ===============================
print_header "API Documentation"

run_test "Get OpenAPI schema" "$BASE_URL/openapi.json"

run_test "Get Swagger UI docs" "$BASE_URL/docs"

run_test "Get ReDoc documentation" "$BASE_URL/redoc"

# ===============================
# EDGE CASES AND VALIDATION
# ===============================
print_header "Edge Cases and Validation"

run_test "Search with empty query" "$BASE_URL/search/items?query="

run_test "Search with special characters" "$BASE_URL/search/items?query=café"

run_test "Search with URL encoded query" "$BASE_URL/search/items?query=chicken%20salad"

run_test "Price filter with zero" "$BASE_URL/search/items?price_gt=0"

run_test "Price filter with decimal" "$BASE_URL/search/items?price_lt=15.50"

run_test "Restaurant name with spaces (URL encoded)" "$BASE_URL/restaurants/$(echo "$RESTAURANT_NAME" | sed 's/ /%20/g')"

run_test "Case sensitivity test for restaurant search" "$BASE_URL/search/items?restaurant=$(echo "$RESTAURANT_NAME" | tr '[:upper:]' '[:lower:]')"

# ===============================
# PERFORMANCE TESTS
# ===============================
print_header "Performance Tests"

run_test "Large limit test (500)" "$BASE_URL/search/items?limit=500"

run_test "Multiple filters combined" "$BASE_URL/search/items?query=chicken&price_gt=5&price_lt=50&sort_by=price&order=desc&limit=20"

# ===============================
# RESULTS SUMMARY
# ===============================
print_header "Test Results Summary"

echo -e "Total tests run: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please check the output above.${NC}"
    exit 1
fi