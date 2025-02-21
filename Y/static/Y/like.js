document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".like-btn").forEach(button => {
        button.addEventListener("click", function () {
            let tweetId = this.dataset.tweet;
            let likeCountSpan = document.getElementById(`like-count-${tweetId}`);
            let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(`/like/${tweetId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                likeCountSpan.textContent = data.like_count;
                this.textContent = data.liked ? "❤️ いいね取消" : "🤍 いいね";
            });
        });
    });
});
