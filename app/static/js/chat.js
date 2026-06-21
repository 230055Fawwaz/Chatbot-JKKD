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
                // Tampilkan jawaban utama dari Qwen
                tampilkanPesan(data.reply, 'bot-message', data.sources);
            } else {
                tampilkanPesan('Waduh, ada masalah di server lokal.', 'bot-message error');
            }

        } catch (error) {
            console.error('Error:', error);
            hapusLoading(loadingId);
            tampilkanPesan('Gagal terhubung ke server Flask. Pastikan Flask menyala.', 'bot-message error');
        }
    });

    function tampilkanPesan(teks, tipeKelas, sources = []) {
        const pesanDiv = document.createElement('div');
        pesanDiv.className = `message ${tipeKelas}`;
        
        // Buat element penampung teks utama
        const teksSpan = document.createElement('span');
        teksSpan.textContent = teks;
        pesanDiv.appendChild(teksSpan);
        
        // JIKA ada data sumber dokumen, tampilkan di bawah teks utama
        if (sources && sources.length > 0) {
            const sumberDiv = document.createElement('div');
            sumberDiv.style.fontSize = '0.78rem';
            sumberDiv.style.color = '#a6adc8';
            sumberDiv.style.marginTop = '8px';
            sumberDiv.style.borderTop = '1px solid #45475a';
            sumberDiv.style.paddingTop = '4px';
            
            // Gabungkan nama file dengan koma
            sumberDiv.innerHTML = `📚 <strong>Sumber materi:</strong> ${sources.join(', ')}`;
            pesanDiv.appendChild(sumberDiv);
        }
        
        // Jika tipeKelas memuat loading status
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