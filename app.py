
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, jsonify
)
import mysql.connector
from datetime import datetime
import math

from ai_chatbot import ask_energy_assistant


app = Flask(__name__)
app.secret_key = "energyq-local-development-key"


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="----",
        database="smart_electricity_db"
    )


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT COALESCE(SUM(units_consumed), 0) AS total_units
            FROM monthly_consumption
        """)
        total_units = float(cursor.fetchone()["total_units"] or 0)

        cursor.execute("""
            SELECT record_id, month_year, units_consumed
            FROM monthly_consumption
            ORDER BY record_id DESC
            LIMIT 2
        """)
        recent_records = cursor.fetchall()

        latest_units = (
            float(recent_records[0]["units_consumed"])
            if recent_records else 0
        )
        estimated_bill = latest_units * 5

        cursor.execute("""
            SELECT month_year, units_consumed
            FROM monthly_consumption
            ORDER BY record_id DESC
        """)
        monthly_records = cursor.fetchall()

        cursor.execute("""
            SELECT appliance_name, monthly_units
            FROM appliances
            ORDER BY monthly_units DESC
        """)
        appliances = cursor.fetchall()

        return render_template(
            "dashboard.html",
            total_units=round(total_units, 2),
            latest_units=round(latest_units, 2),
            estimated_bill=round(estimated_bill, 2),
            recent_records=recent_records,
            monthly_records=monthly_records,
            appliances=appliances
        )

    finally:
        cursor.close()
        connection.close()


# ---------------- BILL CALCULATOR ----------------

@app.route("/bill-calculator", methods=["GET", "POST"])
def bill_calculator():
    bill = None
    error = None
    units = ""
    rate = "5"

    if request.method == "POST":
        units = request.form.get("units", "").strip()
        rate = request.form.get("rate", "5").strip()

        try:
            units_value = float(units)
            rate_value = float(rate)

            if (
                not math.isfinite(units_value)
                or not math.isfinite(rate_value)
                or units_value < 0
                or rate_value < 0
            ):
                raise ValueError

            bill = round(units_value * rate_value, 2)

        except (ValueError, TypeError):
            error = "Please enter valid, non-negative numbers."

    return render_template(
        "bill_calculator.html",
        bill=bill,
        error=error,
        units=units,
        rate=rate
    )


# ---------------- USAGE ANALYSIS ----------------

@app.route("/usage-analysis")
def usage_analysis():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT record_id, month_year, units_consumed
            FROM monthly_consumption
            ORDER BY record_id ASC
        """)
        records = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    total_units = 0
    max_units = 0

    for index, record in enumerate(records):
        current_units = float(record["units_consumed"] or 0)
        record["units_consumed"] = current_units

        total_units += current_units
        max_units = max(max_units, current_units)

        if index == 0:
            record["change"] = None
        else:
            previous_units = float(
                records[index - 1]["units_consumed"]
            )

            if previous_units > 0:
                record["change"] = round(
                    (
                        (current_units - previous_units)
                        / previous_units
                    ) * 100,
                    2
                )
            elif current_units > 0:
                record["change"] = None
            else:
                record["change"] = 0

    return render_template(
        "usage_analysis.html",
        records=records,
        total_units=round(total_units, 2),
        max_units=max_units,
        record_count=len(records)
    )


# ---------------- HIGH USAGE ALERT ----------------

@app.route("/high-usage-alert")
def high_usage_alert():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT record_id, month_year, units_consumed
            FROM monthly_consumption
            ORDER BY record_id DESC
            LIMIT 2
        """)
        records = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    latest = None
    previous = None
    latest_units = 0
    previous_units = 0
    increase_units = 0
    change_percent = None

    alert_status = "insufficient"
    alert_title = "Not enough data yet"
    alert_message = (
        "Add at least two monthly consumption records "
        "to compare usage."
    )

    if len(records) >= 1:
        latest = records[0]
        latest_units = float(latest["units_consumed"] or 0)
        latest["units_consumed"] = latest_units

    if len(records) >= 2:
        previous = records[1]
        previous_units = float(previous["units_consumed"] or 0)
        previous["units_consumed"] = previous_units

        increase_units = round(
            latest_units - previous_units, 2
        )

        if previous_units > 0:
            change_percent = round(
                (increase_units / previous_units) * 100, 2
            )

            if change_percent >= 20:
                alert_status = "high"
                alert_title = "High electricity usage detected!"
                alert_message = (
                    "Your latest consumption is at least 20% "
                    "higher than your previous record. "
                    "Check your appliances."
                )
            else:
                alert_status = "normal"
                alert_title = "No high usage detected"
                alert_message = (
                    "Your latest consumption has not increased "
                    "by 20% or more compared with your previous record."
                )

        elif previous_units == 0 and latest_units > 0:
            alert_status = "high"
            alert_title = "Usage has increased from zero"
            alert_message = (
                "Your previous record was zero units and your "
                "latest record is higher. Review your consumption."
            )
        else:
            alert_status = "normal"
            alert_title = "No high usage detected"
            alert_message = (
                "No increase in consumption was detected."
            )

    return render_template(
        "high_usage_alert.html",
        latest=latest,
        previous=previous,
        latest_units=round(latest_units, 2),
        previous_units=round(previous_units, 2),
        increase_units=increase_units,
        change_percent=change_percent,
        alert_status=alert_status,
        alert_title=alert_title,
        alert_message=alert_message
    )


# ---------------- ADD MONTHLY CONSUMPTION ----------------

@app.route("/add-consumption", methods=["GET", "POST"])
def add_consumption():
    if request.method == "POST":
        month_year = request.form.get(
            "month_year", ""
        ).strip()
        units_text = request.form.get(
            "units_consumed", ""
        ).strip()

        try:
            selected_month = datetime.strptime(
                month_year, "%Y-%m"
            )

            if selected_month.strftime("%Y-%m") != month_year:
                raise ValueError

        except ValueError:
            flash(
                "Please select a valid month and year.",
                "error"
            )
            return render_template("add_consumption.html")

        try:
            units = float(units_text)

            if not math.isfinite(units) or units < 0:
                raise ValueError

        except (ValueError, TypeError):
            flash(
                "Please enter a valid, non-negative number of units.",
                "error"
            )
            return render_template("add_consumption.html")

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT record_id
                FROM monthly_consumption
                WHERE month_year = %s
                LIMIT 1
            """, (month_year,))

            if cursor.fetchone():
                flash(
                    "A record for this month already exists. "
                    "Please select another month.",
                    "error"
                )
                return render_template("add_consumption.html")

            cursor.execute("""
                INSERT INTO monthly_consumption
                    (user_id, month_year, units_consumed)
                VALUES (%s, %s, %s)
            """, (1, month_year, units))

            connection.commit()

            flash(
                f"Successfully saved {units:g} units for {month_year}!",
                "success"
            )
            return redirect(url_for("add_consumption"))

        except mysql.connector.Error:
            connection.rollback()
            flash(
                "Database error while saving. "
                "Please check the database.",
                "error"
            )
            return render_template("add_consumption.html")

        finally:
            cursor.close()
            connection.close()

    return render_template("add_consumption.html")


# ---------------- VIEW ALL CONSUMPTION RECORDS ----------------

@app.route("/view-records")
def view_records():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT record_id, user_id, month_year, units_consumed
            FROM monthly_consumption
            ORDER BY record_id DESC
        """)
        records = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    total_units = sum(
        float(record["units_consumed"] or 0)
        for record in records
    )

    return render_template(
        "view_records.html",
        records=records,
        total_units=round(total_units, 2),
        record_count=len(records)
    )


# ---------------- EDIT CONSUMPTION RECORD ----------------

@app.route("/edit-record/<int:record_id>", methods=["GET", "POST"])
def edit_record(record_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT record_id, month_year, units_consumed
            FROM monthly_consumption
            WHERE record_id = %s
        """, (record_id,))

        record = cursor.fetchone()

        if record is None:
            flash("Consumption record not found.", "error")
            return redirect(url_for("view_records"))

        if request.method == "POST":
            units_text = request.form.get(
                "units_consumed", ""
            ).strip()

            try:
                units = float(units_text)

                if not math.isfinite(units) or units < 0:
                    raise ValueError

            except (ValueError, TypeError):
                flash(
                    "Please enter a valid, non-negative number of units.",
                    "error"
                )
                return render_template(
                    "edit_record.html", record=record
                )

            try:
                cursor.execute("""
                    UPDATE monthly_consumption
                    SET units_consumed = %s
                    WHERE record_id = %s
                """, (units, record_id))

                connection.commit()

                flash(
                    f"Record for {record['month_year']} "
                    "updated successfully!",
                    "success"
                )
                return redirect(url_for("view_records"))

            except mysql.connector.Error:
                connection.rollback()
                flash(
                    "Unable to update the record. "
                    "Please check the database.",
                    "error"
                )
                return render_template(
                    "edit_record.html", record=record
                )

        return render_template("edit_record.html", record=record)

    finally:
        cursor.close()
        connection.close()


# ---------------- DELETE CONSUMPTION RECORD ----------------

@app.route("/delete-record/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            DELETE FROM monthly_consumption
            WHERE record_id = %s
        """, (record_id,))

        if cursor.rowcount == 0:
            flash(
                "Record not found. Nothing was deleted.",
                "error"
            )
        else:
            connection.commit()
            flash(
                "Consumption record deleted successfully.",
                "success"
            )

    except mysql.connector.Error:
        connection.rollback()
        flash(
            "Unable to delete the record. "
            "Please check the database.",
            "error"
        )

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("view_records"))


# ---------------- AI ENERGY CHATBOT ----------------

@app.route("/ai-chatbot")
def ai_chatbot_page():
    return render_template("ai_chatbot.html")


@app.route("/api/ai-chat", methods=["POST"])
def ai_chat_api():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "error": "Please enter a question."
        }), 400

    if len(question) > 1000:
        return jsonify({
            "error": "Your question must be 1000 characters or fewer."
        }), 400

    answer = ask_energy_assistant(question.strip())

    return jsonify({
        "answer": answer
    })


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)
