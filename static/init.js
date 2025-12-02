const accuracySlider = document.getElementById("accuracy");
    const accuracyValue = document.getElementById("accuracy-value");

    accuracySlider.addEventListener("input", () => {
      accuracyValue.textContent = `${accuracySlider.value}%`;
    });

    document.getElementById("search-form").addEventListener("submit", (event) => {
      event.preventDefault();
      const query = event.target.query.value;
      const accuracy = accuracySlider.value;
      // Добавьте обработку с учетом точности:
      console.log("Запрос:", query, "Точность:", accuracy);
      // TODO: передайте точность в backend или используйте для фильтрации
    });
    const settingsBtn = document.getElementById('settingsBtn');
    const settingsMenu = document.getElementById('settingsMenu');
    const indexBtn = settingsMenu.querySelector('button[form="index-form"]');

    // Показ/скрытие меню
    settingsBtn.addEventListener('click', (event) => {
      event.stopPropagation();
      settingsMenu.classList.toggle('hidden');
    });

    // Клик по "Проиндексировать"
    indexBtn.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();

      // Спрятать кнопку (без удаления из DOM!)
      // indexBtn.hidden = true;

      // Спрятать меню
      settingsMenu.classList.add('hidden');

      // Отправить форму
      document.getElementById('index-form')?.requestSubmit?.();
    });

    // Клик вне — закрыть меню
    document.addEventListener('click', (event) => {
      if (!settingsMenu.contains(event.target) && !settingsBtn.contains(event.target)) {
        settingsMenu.classList.add('hidden');
      }
    });
    function updateAccuracyValue(val) {
        document.getElementById('accuracy-value').textContent = val + '%';
      }

      function appendAccuracy(formId) {
        const form = document.getElementById(formId);
        const existing = form.querySelector('input[name="accuracy"]');
        if (existing) existing.remove();  // убираем старые, если есть
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'accuracy';
        input.value = document.getElementById('accuracy').value;
        form.appendChild(input);
      }

      document.getElementById('search-form').addEventListener('submit', function () {
        appendAccuracy('search-form');
      });

      document.getElementById('upload-form').addEventListener('submit', function () {
        appendAccuracy('upload-form');
      });

