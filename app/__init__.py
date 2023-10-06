from flask import Flask, request, jsonify
from random import randint
from math import ceil

app = Flask(__name__)

receipts = {}

@app.route('/')
def index():
    return '<h1>Fetch Rewards Take Home Assessment</h1>'

def generate_id():
    '''
    returns a random id in xxxxxxxx-xxxx-xxxx-xxxxxxxxxxxx format
    '''
    id = ""
    chars = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    id_lens = [8, 4, 4, 12]

    for id_len in id_lens:
        for i in range(id_len):
            id += chars[randint(0, 61)]

        if id_len != 12:
            id += "-"

    return id

# route for testing purposes to view all processed receipts
@app.route('/receipts/all')
def all_receipts():
    print(receipts)
    return receipts

# route for getting a receipt's points by id
@app.route('/receipts/<string:id>/points')
def get_points(id):
    '''
    Returns the points for the receipt with the passed in ID
    '''
    points = 0

    # verify that the receipt exists
    if id not in receipts:
        return jsonify({"error": "No receipt found for that id"}), 400

    receipt = receipts[id]

    # determine the points for the receipt
    # Rule 1: One point for every alphanumeric character in the retailer name.
    retailer = receipt["retailer"]

    for i in range(len(retailer)):
        chars = list(retailer)
        if chars[i].isalnum():
            points += 1

    # Rule 2: 50 points if the total is a round dollar amount with no cents.
    total = receipt["total"]
    total_parts = total.split(".")
    if total_parts[1] == "00":
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25.
    cents = int(total_parts[1])
    if cents % 25 == 0:
        points += 25

    # Rule 4: 5 points for every two items on the receipt.
    items = receipt["items"]
    item_count = 0

    for item in items:
        item_count += 1

    points += 5 * (item_count//2)

    # Rule 5: If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer. The result is the number of points earned.
    for item in items:
        description = item["shortDescription"].strip()
        price = float(item["price"])

        if len(description) % 3 == 0:
            points += ceil(price * 0.2)

    # Rule 6: 6 points if the day in the purchase date is odd.
    date = receipt["purchaseDate"]
    date_parts = date.split("-")
    day = int(date_parts[2])
    if day % 2 == 1:
        points += 6

    # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm.
    time = receipt["purchaseTime"]
    time_parts = time.split(":")
    hours = int(time_parts[0])
    minutes = int(time_parts[1])

    if hours >= 14 and hours < 16:
        points += 10

    return jsonify({"points": points})

# route for processing receipts and giving them an id
@app.route('/receipts/process', methods=['POST'])
def process_receipts():
    '''
    Takes in a JSON receipt and returns a JSON object with a generated ID
    '''
    receipt = request.get_json()

    keys = ["retailer", "purchaseDate", "purchaseTime", "total", "items"]

    # validate the receipt
    for key in keys:
        # check the presence of all keys
        if key not in receipt:
            return jsonify({"error": "The receipt is invalid"}), 400

        # validate the purchase date
        if key == "purchaseDate":
            date_parts = receipt[key].split("-")

            # 3 parts in the date check
            if len(date_parts) != 3:
                return jsonify({"error": "The receipt's date is invalid"}), 400

            # 4 digits for year check
            if len(date_parts[0]) != 4:
                return jsonify({"error": "The receipt's year is invalid"}), 400

            # year is a digit check
            if not date_parts[0].isdigit():
                return jsonify({"error": "The receipt's year is invalid"}), 400

            # 2 digits for month check
            if len(date_parts[1]) != 2:
                return jsonify({"error": "The receipt's month is invalid"}), 400

            # month is a digit check
            if not date_parts[1].isdigit():
                return jsonify({"error": "The receipt's month is invalid"}), 400

            # 2 digits for day check
            if len(date_parts[2]) != 2:
                return jsonify({"error": "The receipt's day is invalid"}), 400

            # day is a digit check
            if not date_parts[2].isdigit():
                return jsonify({"error": "The receipt's day is invalid"}), 400

            # can also do comparisons against today's date to ensure the receipt is from the past

        # validate purchase time
        if key == "purchaseTime":
            time_parts = receipt[key].split(":")

            # 2 parts in time check
            if len(time_parts) != 2:
                return jsonify({"error": "The receipt's time is invalid"}), 400

            # hours is a digit check
            if not time_parts[0].isdigit():
                return jsonify({"error": "The receipt's hour is invalid"}), 400

            # hours is less than 24 check:
            if int(time_parts[0]) > 24:
                return jsonify({"error": "The receipt's hour is invalid"}), 400

            # minutes is a digit check
            if not time_parts[1].isdigit():
                return jsonify({"error": "The receipt's minute is invalid"}), 400

            # minutess is less than 59 check:
            if int(time_parts[1]) > 59:
                return jsonify({"error": "The receipt's minute is invalid"}), 400

        # validate the total
        if key == "total":
            total_parts = receipt[key].split(".")

            # 2 parts in total check
            if len(total_parts) != 2:
                return jsonify({"error": "The receipt's total is invalid"}), 400

            # dollars is a digit check
            if not total_parts[0].isdigit():
                return jsonify({"error": "The receipt's dollar total is invalid"}), 400

            # cents is a digit check
            if not total_parts[1].isdigit():
                return jsonify({"error": "The receipt's cent total is invalid"}), 400

            # cents are less than 100 check:
            if int(total_parts[1]) > 99:
                return jsonify({"error": "The receipt's cent total is invalid"}), 400

            # cents are 2 digits check:
            if len(total_parts[1]) != 2:
                return jsonify({"error": "The receipt's cent total is invalid"}), 400

        if key == "items":
            for item in receipt[key]:
                price = item["price"]

                # validate the prices or each item just like with total
                price_parts = price.split(".")

                # 2 parts in price check
                if len(price_parts) != 2:
                    return jsonify({"error": "The receipt's item's prices is invalid"}), 400

                # dollars is a digit check
                if not price_parts[0].isdigit():
                    return jsonify({"error": "The receipt's item's dollar price is invalid"}), 400

                # cents is a digit check
                if not price_parts[1].isdigit():
                    return jsonify({"error": "The receipt's item's cent price is invalid"}), 400

                # cents are less than 100 check:
                if int(price_parts[1]) > 99:
                    return jsonify({"error": "The receipt's item's cent price is invalid"}), 400

                # cents are 2 digits check:
                if len(price_parts[1]) != 2:
                    return jsonify({"error": "The receipt's item's cent price is invalid"}), 400

    # generate the id for the receipt and store it in the receipts dict w/ the id as the key and the receipt as the value
    id = generate_id()
    receipts[id] = receipt

    return jsonify({"id": id})
