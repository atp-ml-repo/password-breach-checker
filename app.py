from flask import Flask, render_template, request, jsonify
import hashlib
import requests

app = Flask(__name__)


def check_password_breach(password):
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    first5_chars = sha1_password[:5]
    response = requests.get(f'https://api.pwnedpasswords.com/range/{first5_chars}')

    if response.status_code != 200:
        raise RuntimeError(f'Error fetching data: {response.status_code}')

    hashes = (line.split(':') for line in response.text.splitlines())
    for suffix, count in hashes:
        if sha1_password[5:] == suffix:
            return True, sha1_password, int(count)

    return False, sha1_password, 0


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        password = request.form['password']
        is_breached, full_hash, count = check_password_breach(password)
        probability = min(1, count / 1000000)  # Probability estimate based on 1 million hashes

        return render_template('index.html',
                               is_breached=is_breached,
                               full_hash=full_hash,
                               count=count,
                               probability=probability)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
