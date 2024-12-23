document.addEventListener('DOMContentLoaded', () => {
    // Обработчик для сортировки
    const sortForm = document.getElementById('sort-form');
    const sortBySelect = document.getElementById('sort_by');

    sortForm.addEventListener('change', async (e) => {
        e.preventDefault();
        const sortBy = sortBySelect.value;

        // Получаем отсортированные данные с сервера через AJAX
        const response = await fetch(`/sort?sort_by=${sortBy}`);
        const data = await response.json();

        // Обновляем список бетономешалок
        const betonomehalkaList = document.getElementById('betonomehalka-list');
        betonomehalkaList.innerHTML = '';  // Очищаем текущий список

        // Заполняем новый список
        data.betonomehalkers.forEach(item => {
            const li = document.createElement('li');
            li.id = `betonomehalka-${item.id}`;
            li.innerHTML = `
                <h2>${item.name}</h2>
                <p>${item.specs}</p>
                <p>Цена: ${item.price} руб</p>
                <form class="comment-form" data-id="${item.id}">
                    <input type="text" name="text" placeholder="Оставьте комментарий">
                    <button type="submit">Отправить</button>
                </form>
                <ul id="comments-${item.id}">
                    ${item.comments.map(comment => `<li>${comment.text}</li>`).join('')}
                </ul>
            `;
            betonomehalkaList.appendChild(li);
        });
    });

    // Обработчик для отправки комментариев
    document.querySelectorAll('.comment-form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const betonomehalkaId = form.dataset.id;
            const text = form.querySelector('input[name="text"]').value;

            // Отправляем комментарий на сервер
            const response = await fetch('/comment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ betonomehalka_id: betonomehalkaId, text })
            });

            const result = await response.json();
            if (result.success) {
                alert(result.message);

                // Обновляем список комментариев на странице
                const commentList = document.getElementById(`comments-${betonomehalkaId}`);
                const newComment = document.createElement('li');
                newComment.textContent = result.text;
                commentList.appendChild(newComment);
            } else {
                alert(result.message);
            }
        });
    });
});
