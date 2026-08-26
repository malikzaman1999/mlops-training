"""
Model Prediction Script

Makes predictions using deployed Azure ML endpoint.
"""

import argparse
import json
import requests
import time

from utils import get_ml_client


def predict(endpoint_name, data, deployment_name=None):
    """
    Make prediction using Azure ML endpoint.

    Args:
        endpoint_name: Name of the endpoint
        data: Input data as list of lists (e.g., [[2500, 3, 2, 1995, 1, 0, 8]])
        deployment_name: Optional specific deployment to test

    Returns:
        Prediction result
    """
    ml_client = get_ml_client()

    print("="*70)
    print("Making Prediction")
    print("="*70)

    # Get endpoint details
    endpoint = ml_client.online_endpoints.get(name=endpoint_name)

    print(f"\nEndpoint: {endpoint_name}")
    print(f"  Scoring URI: {endpoint.scoring_uri}")

    if deployment_name:
        print(f"  Targeting deployment: {deployment_name}")
    else:
        print(f"  Using traffic split")

    # Get API key
    keys = ml_client.online_endpoints.get_keys(name=endpoint_name)
    api_key = keys.primary_key

    # Prepare request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "data": data
    }

    print(f"\nInput data:")
    print(f"  {data}")

    # Make request
    start_time = time.time()

    if deployment_name:
        # Test specific deployment
        result = ml_client.online_endpoints.invoke(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            request_file=json.dumps(payload)
        )
    else:
        # Use traffic split
        response = requests.post(
            endpoint.scoring_uri,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()

    latency = (time.time() - start_time) * 1000  # Convert to ms

    print(f"\n✓ Prediction successful!")
    print(f"  Result: {result}")
    print(f"  Latency: {latency:.0f}ms")

    # If result is a price, format nicely
    if isinstance(result, (list, tuple)) and len(result) > 0:
        price = result[0]
        print(f"\n  Predicted Price: ${price:,.2f}")

    print("\n" + "="*70)

    return result


def main():
    parser = argparse.ArgumentParser(description="Make predictions using deployed model")
    parser.add_argument("--endpoint", type=str, default="housing-endpoint",
                       help="Endpoint name")
    parser.add_argument("--deployment", type=str,
                       help="Specific deployment to test (optional)")
    parser.add_argument("--data", type=str,
                       help="Input data as JSON list, e.g., '[[2500, 3, 2, 1995, 1, 0, 8]]'")

    args = parser.parse_args()

    # Default sample data if not provided
    if args.data:
        data = json.loads(args.data)
    else:
        # Sample: [sqft, bedrooms, bathrooms, year_built, has_garage, has_pool, location_score]
        data = [[2500, 3, 2, 1995, 1, 0, 8]]
        print("Using default sample data (2500 sqft, 3 bed, 2 bath, built 1995, garage, no pool, location 8/10)")

    predict(args.endpoint, data, args.deployment)


if __name__ == "__main__":
    main()
