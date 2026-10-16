import os
import stripe
from flask import Flask, render_template, request, jsonify, redirect

app = Flask(__name__)

# Configura tu llave secreta de Stripe leyendo la variable de entorno
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-checkout-session', methods=['GET', 'POST'])
def create_checkout_session():
    try:
        # URL base de tu aplicación en Render
        domain_url = "https://studio-ai-app.onrender.com"
        
        # Crear la sesión de pago oficial en Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'StudioAI PRO',
                    },
                    'unit_amount': 100, # Representa $1.00 USD en centavos
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=domain_url + '/?success=true',
            cancel_url=domain_url + '/?canceled=true',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/generate-text-to-video', methods=['POST'])
def generate_text_to_video():
    try:
        mode = request.form.get('mode')
        prompt = request.form.get('prompt')
        return jsonify({
            "success": True,
            "media_url": "https://www.w3schools.com/html/mov_bbb.mp4"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/generate-instagram-image', methods=['POST'])
def generate_instagram_image():
    try:
        insta_prompt = request.form.get('insta_prompt')
        return jsonify({
            "success": True,
            "media_url": "https://via.placeholder.com/512.png"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/generate-music', methods=['POST'])
def generate_music():
    try:
        music_prompt = request.form.get('music_prompt')
        lyrics = request.form.get('lyrics')
        return jsonify({
            "success": True,
            "media_url": "https://www.w3schools.com/html/horse.ogg"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
