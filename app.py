import os
import base64
import stripe
import replicate
from flask import Flask, render_template, request, jsonify, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_super_segura'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

os.environ["REPLICATE_API_TOKEN"] = os.environ.get("AI_API_KEY", "r8_8Cz4EWqGPAxUyJcsWOT7j4KIMCu75TV0eSAQG")
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_tu_clave_secreta_de_stripe")

def file_to_data_uri(filepath):
    with open(filepath, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    ext = filepath.split(".")[-1].lower()
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{encoded}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Suscripción Mensual Studio AI',
                    },
                    'unit_amount': 100,
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url='http://127.0.0.1:5000/?success=true',
            cancel_url='http://127.0.0.1:5000/?canceled=true',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/generate-text-to-video', methods=['POST'])
def generate_text_to_video():
    mode = request.form.get('mode', 'avatar')
    prompt = request.form.get('prompt', '').strip()
    avatar = request.form.get('avatar', 'default')
    product_name = request.form.get('product_name', 'Producto destacado').strip()
    product_features = request.form.get('product_features', 'Alta calidad y diseño exclusivo').strip()

    if mode == 'tiktok_product' and not product_name:
        return jsonify({'error': 'El nombre del producto es obligatorio para TikTok'}), 400

    try:
        image_uri = None

        if 'product_image' in request.files and request.files['product_image'].filename != '':
            file = request.files['product_image']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_uri = file_to_data_uri(filepath)

        # Si el usuario subió una imagen, usamos p-video-animate para mayor dinamismo
        if image_uri:
            output = replicate.run(
                "prunaai/p-video-animate",
                input={
                    "image": image_uri,
                    "video": "https://replicate.delivery/pbxt/PHimTe4wXb4rdubakhmVFEhK7m01BMKRfYON89Ncvt2Ib36Q/gaming_animate_commander_scene_skin_driver.mp4"
                }
            )
        else:
            if mode == 'tiktok_product':
                style_desc = "Vertical 9:16 format, stunning macro cinematic product showcase, luxury studio lighting, 4k."
                full_prompt = f"Viral TikTok ad for '{product_name}'. {product_features}. {prompt} {style_desc}"
            else:
                full_prompt = f"Professional speaker talking to camera, realistic studio lighting. {prompt}"

            output = replicate.run(
                "luma/ray-3.2",
                input={"prompt": full_prompt, "aspect_ratio": "9:16"}
            )

        video_url = output.url if hasattr(output, 'url') else str(output)

        if video_url:
            return jsonify({'success': True, 'media_url': video_url, 'type': 'video'})
        else:
            return jsonify({'error': 'No se pudo obtener la URL del video generado.'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-instagram-image', methods=['POST'])
def generate_instagram_image():
    prompt = request.form.get('insta_prompt', '').strip()
    if not prompt:
        return jsonify({'error': 'La descripción de la imagen es obligatoria'}), 400

    try:
        output = replicate.run(
            "google/nano-banana-2",
            input={
                "prompt": f"Aesthetic Instagram viral post image, {prompt}, 8k resolution, photorealistic.",
                "aspect_ratio": "1:1"
            }
        )
        image_url = output.url if hasattr(output, 'url') else str(output)
        return jsonify({'success': True, 'media_url': image_url, 'type': 'image'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-music', methods=['POST'])
def generate_music():
    lyrics = request.form.get('lyrics', '').strip()
    prompt = request.form.get('music_prompt', '').strip()

    if not prompt:
        return jsonify({'error': 'El estilo musical es obligatorio'}), 400

    try:
        music_input = {"prompt": prompt}
        if lyrics:
            music_input["lyrics"] = lyrics

        output = replicate.run(
            "minimax/music-2.6",
            input=music_input
        )
        music_url = output.url if hasattr(output, 'url') else str(output)
        return jsonify({'success': True, 'media_url': music_url, 'type': 'audio'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)