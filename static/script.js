document.addEventListener('DOMContentLoaded', function() {
    // Инициализация выбора даты с помощью flatpickr
    flatpickr("#date", {
        enableTime: false,
        dateFormat: "Y-m-d",
    });

    // Обработка отправки формы
    document.getElementById('flight-form').addEventListener('submit', function(event) {
        event.preventDefault();

        let destination = document.getElementById('destination').value;
        let date = document.getElementById('date').value;

        // Отправка POST-запроса для получения прогноза погоды
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `destination=${destination}&date=${date}`,
        })
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('results');

            if (data.error) {
                resultsDiv.innerText = data.error;
            } else {
                // Применение фона и эффектов на основе погоды
                applyWeatherBackground(data.weather[0].weather);

                // Формирование HTML с информацией о погоде
                let html = `<h3>Прогноз погоды в ${destination} на ${date}</h3>`;
                html += `
                    <p>Дата: ${data.weather[0].date}</p>
                    <p>Температура: ${data.weather[0].temperature.toFixed(2)} C</p>
                    <p>Давление: ${data.weather[0].pressure.toFixed(2)} hPa</p>
                    <p>Влажность: ${data.weather[0].humidity.toFixed(2)}%</p>
                    <p>Скорость ветра: ${data.weather[0].wind_speed.toFixed(2)} м/с</p>
                    <p>Погода: ${data.weather[0].weather}</p>
                    <p>Рекомендуемый гардероб:</p>
                    <div class="wardrobe-images">
                        ${data.weather[0].wardrobe_images.map(image => `<img src="/static/images/wardrobe/${image}" alt="Wardrobe Image" class="img-fluid wardrobe-img">`).join('')}
                    </div>
                    <hr>
                `;
                resultsDiv.innerHTML = html;

                // Отображение предупреждений о погоде
                showWeatherAlert(data.weather[0].weather);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Функция для изменения фона и эффектов на основе погоды
    function applyWeatherBackground(weather) {
        const body = document.querySelector('body');
        const rainEffect = document.querySelector('.rain');
        body.className = ''; // Сброс классов
        rainEffect.style.display = 'none'; // Скрываем дождь по умолчанию

        // Применение соответствующих эффектов в зависимости от погоды
        if (weather.includes('rain')) {
            body.classList.add('rain');
            rainEffect.style.display = 'block'; // Показать эффект дождя
        } else if (weather.includes('clear')) {
            body.classList.add('clear');
        } else if (weather.includes('snow')) {
            body.classList.add('snow');
        } else if (weather.includes('wind')) {
            body.classList.add('wind');
        }
    }

    // Функция для отображения предупреждений о погоде
    function showWeatherAlert(weather) {
        const alerts = document.querySelectorAll('.weather-alert');
        alerts.forEach(alert => alert.classList.remove('show')); // Скрываем все предупреждения

        // Отображение соответствующих предупреждений
        if (weather.includes('rain')) {
            displayAlert('rain');
        } else if (weather.includes('snow')) {
            displayAlert('snow');
        } else if (weather.includes('wind')) {
            displayAlert('wind');
        }
    }

    // Функция для добавления класса "show" к нужному предупреждению
    function displayAlert(condition) {
        const alert = document.querySelector(`.weather-alert.alert-${condition}`);
        if (alert) {
            alert.classList.add('show');
        }
    }
});


