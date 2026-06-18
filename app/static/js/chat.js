// ==========================================
// Nama File: chat.js
// Deskripsi: JS bagi chat.html
// Penulis:   Fawwaz Yaqzhan
// Tanggal:   18-06-2026
// Catatan:
//   - Mengatur interaksi user di chat.html
// ==========================================

// app/static/js/chat.js

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatBox = document.getElementById('chatBox');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Mencegah page reload

        const pesanUser = userInput.value.trim();
        if (!pesanUser) return;

        // 1. Tampilkan pesan user ke layar chat
        tampilkanPesan(pesanUser, 'user-message');
        userInput.value = ''; // Kosongkan input

        // 2. Tampilkan status "Sedang berpikir..."
        const loadingId = tampilkanPesan('Typing...', 'bot-message loading');

        try {
            // 3. Kirim data ke API Flask
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: pesanUser })
            });

            const data = await response.json();
            
            // Hapus tulisan "Typing..."
            hapusLoading(loadingId);

            if (data.status === 'success') {
                // 4. Tampilkan jawaban dari Qwen RAG
                tampilkanPesan(data.reply, 'bot-message');
            } else {
                tampilkanPesan('Waduh, ada masalah di server lokal.', 'bot-message error');
            }

        } catch (error) {
            console.error('Error:', error);
            hapusLoading(loadingId);
            tampilkanPesan('Gagal terhubung ke server Flask. Pastikan Flask menyala.', 'bot-message error');
        }
    });

    function tampilkanPesan(teks, tipeKelas) {
        const pesanDiv = document.createElement('div');
        pesanDiv.className = `message ${tipeKelas}`;
        pesanDiv.innerText = teks;
        
        // Berikan ID acak jika ini status loading agar mudah dihapus nanti
        if (tipeKelas.includes('loading')) {
            const idUnique = 'load-' + Date.now();
            pesanDiv.id = idUnique;
            chatBox.appendChild(pesanDiv);
            gulungKeBawah();
            return idUnique;
        }

        chatBox.appendChild(pesanDiv);
        gulungKeBawah();
    }

    function hapusLoading(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function gulungKeBawah() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});