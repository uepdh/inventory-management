"""
Tests for restocking API endpoints.
"""
import pytest


class TestRestockRecommendationsEndpoint:
    """Test suite for GET /api/restocking/recommendations."""

    def test_get_recommendations_structure(self, client):
        """Test getting restock recommendations returns expected structure."""
        response = client.get("/api/restocking/recommendations?budget=5000")
        assert response.status_code == 200

        data = response.json()
        assert data["budget"] == 5000
        assert "total_estimated_cost" in data
        assert "remaining_budget" in data
        assert isinstance(data["items"], list)

    def test_recommendation_item_fields(self, client):
        """Test that each recommendation has the required fields."""
        response = client.get("/api/restocking/recommendations?budget=10000")
        data = response.json()
        assert len(data["items"]) > 0

        for item in data["items"]:
            assert "item_sku" in item
            assert "item_name" in item
            assert "current_demand" in item
            assert "forecasted_demand" in item
            assert "trend" in item
            assert "unit_cost" in item
            assert "lead_time_days" in item
            assert "recommended_quantity" in item
            assert "estimated_cost" in item
            assert "fully_funded" in item
            assert item["recommended_quantity"] > 0

    def test_recommendations_only_include_items_with_demand_gap(self, client):
        """Test that only items forecast to need more stock are recommended."""
        response = client.get("/api/restocking/recommendations?budget=100000")
        data = response.json()

        for item in data["items"]:
            assert item["forecasted_demand"] > item["current_demand"]

    def test_recommendations_prioritize_largest_demand_gap(self, client):
        """Test that recommendations are ranked by demand gap descending."""
        response = client.get("/api/restocking/recommendations?budget=100000")
        items = response.json()["items"]
        assert len(items) > 1

        gaps = [item["forecasted_demand"] - item["current_demand"] for item in items]
        assert gaps == sorted(gaps, reverse=True)

    def test_recommendations_respect_budget(self, client):
        """Test that total estimated cost never exceeds the given budget."""
        response = client.get("/api/restocking/recommendations?budget=500")
        data = response.json()

        assert data["total_estimated_cost"] <= 500
        calculated_total = round(sum(item["estimated_cost"] for item in data["items"]), 2)
        assert abs(calculated_total - data["total_estimated_cost"]) < 0.01
        assert abs(data["remaining_budget"] - (500 - data["total_estimated_cost"])) < 0.01

    def test_recommendations_zero_budget_returns_no_items(self, client):
        """Test that a zero budget produces no recommendations."""
        response = client.get("/api/restocking/recommendations?budget=0")
        assert response.status_code == 200

        data = response.json()
        assert data["items"] == []
        assert data["total_estimated_cost"] == 0

    def test_recommendations_negative_budget_rejected(self, client):
        """Test that a negative budget is rejected."""
        response = client.get("/api/restocking/recommendations?budget=-100")
        assert response.status_code == 400

    def test_recommendations_missing_budget_rejected(self, client):
        """Test that omitting the required budget param is rejected."""
        response = client.get("/api/restocking/recommendations")
        assert response.status_code == 422


class TestRestockOrdersEndpoint:
    """Test suite for GET/POST /api/restocking/orders."""

    def test_get_restocking_orders_returns_list(self, client):
        """Test that restocking orders are returned as a list."""
        response = client.get("/api/restocking/orders")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_restocking_order(self, client):
        """Test submitting a restocking order from recommended items."""
        recs = client.get("/api/restocking/recommendations?budget=5000").json()["items"]
        assert len(recs) > 0

        payload = {
            "budget": 5000,
            "items": [
                {"item_sku": recs[0]["item_sku"], "quantity": recs[0]["recommended_quantity"]}
            ]
        }
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert order["order_number"].startswith("RST-")
        assert order["status"] == "Submitted"
        assert len(order["items"]) == 1
        assert order["items"][0]["item_sku"] == recs[0]["item_sku"]
        assert order["total_cost"] == order["items"][0]["line_total"]
        assert order["lead_time_days"] == recs[0]["lead_time_days"]
        assert "T" in order["order_date"]
        assert "T" in order["expected_delivery"]

    def test_created_order_appears_in_list(self, client):
        """Test that a submitted order shows up in the restocking orders list."""
        recs = client.get("/api/restocking/recommendations?budget=5000").json()["items"]
        payload = {
            "budget": 5000,
            "items": [{"item_sku": recs[0]["item_sku"], "quantity": 1}]
        }
        create_response = client.post("/api/restocking/orders", json=payload)
        order_number = create_response.json()["order_number"]

        list_response = client.get("/api/restocking/orders")
        order_numbers = [order["order_number"] for order in list_response.json()]
        assert order_number in order_numbers

    def test_create_order_with_unknown_sku_fails(self, client):
        """Test that ordering an unknown SKU returns 404."""
        payload = {"budget": 1000, "items": [{"item_sku": "NOT-A-REAL-SKU", "quantity": 5}]}
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 404

    def test_create_order_with_zero_quantity_fails(self, client):
        """Test that a non-positive quantity is rejected."""
        recs = client.get("/api/restocking/recommendations?budget=5000").json()["items"]
        payload = {"budget": 1000, "items": [{"item_sku": recs[0]["item_sku"], "quantity": 0}]}
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 400

    def test_create_order_with_no_items_fails(self, client):
        """Test that an order with an empty items list is rejected."""
        response = client.post("/api/restocking/orders", json={"budget": 1000, "items": []})
        assert response.status_code == 400

    def test_order_lead_time_is_max_of_line_items(self, client):
        """Test that a multi-item order's lead time is the slowest item's lead time."""
        forecasts = client.get("/api/demand").json()
        two_items = sorted(forecasts, key=lambda f: f["lead_time_days"])[:2]

        payload = {
            "budget": 100000,
            "items": [{"item_sku": f["item_sku"], "quantity": 1} for f in two_items]
        }
        response = client.post("/api/restocking/orders", json=payload)
        order = response.json()

        assert order["lead_time_days"] == max(f["lead_time_days"] for f in two_items)
