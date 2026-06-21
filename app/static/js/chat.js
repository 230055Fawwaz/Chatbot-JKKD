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
    const newChatBtn = document.getElementById('newChatBtn');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const pesanUser = userInput.value.trim();
        if (!pesanUser) return;

        tampilkanPesan(pesanUser, 'user-message');
        userInput.value = '';

        // Tampilkan loading statis sementara
        const loadingId = tampilkanPesan('Menghubungi AI...', 'bot-message loading');

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: pesanUser })
            });

            // Hapus status loading awal
            hapusLoading(loadingId);

            // Buat gelembung chat kosong untuk menampung teks yang akan mengalir
            const pesanDiv = document.createElement('div');
            pesanDiv.className = 'message bot-message';
            const teksSpan = document.createElement('span');
            pesanDiv.appendChild(teksSpan);
            chatBox.appendChild(pesanDiv);

            // Mulai membaca data stream dari Flask
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let sourcesData = [];

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                // Dekode biner menjadi teks string
                const chunk = decoder.decode(value, { stream: true });
                
                // Pisahkan baris karena format SSE diawali dengan "data: "
                const lines = chunk.split('\n');
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const rawJson = line.replace('data: ', '').trim();
                        try {
                            const parsed = JSON.parse(rawJson);
                            
                            if (parsed.type === 'sources') {
                                sourcesData = parsed.content;
                            } else if (parsed.type === 'token') {
                                // Tambahkan kata baru ke dalam gelembung chat secara real-time
                                teksSpan.textContent += parsed.content;
                                chatBox.scrollTop = chatBox.scrollHeight; // Auto scroll otomatis
                            } else if (parsed.type === 'text') {
                                teksSpan.textContent = parsed.content;
                            }
                        } catch (e) {
                            // Abaikan jika ada json chunk yang belum utuh di ujung baris
                        }
                    }
                }
            }

            // Setelah stream teks selesai, jika ada sumber dokumen, tempel di bagian bawah
            if (sourcesData && sourcesData.length > 0) {
                const sumberDiv = document.createElement('div');
                sumberDiv.style.fontSize = '0.78rem';
                sumberDiv.style.color = '#a6adc8';
                sumberDiv.style.marginTop = '8px';
                sumberDiv.style.borderTop = '1px solid #45475a';
                sumberDiv.style.paddingTop = '4px';
                sumberDiv.innerHTML = `📚 <strong>Sumber materi:</strong> ${sourcesData.join(', ')}`;
                pesanDiv.appendChild(sumberDiv);
            }

        } catch (error) {
            console.error('Error:', error);
            hapusLoading(loadingId);
            tampilkanPesan('Gagal terhubung ke server.', 'bot-message error');
        }
    });

    newChatBtn.addEventListener('click', () => {
        // 1. Kosongkan seluruh isi chatBox
        chatBox.innerHTML = '';

        // 2. Tampilkan kembali pesan sambutan awal dari bot
        const pesanAwal = "Halo! Aku asisten kuliah lokalmu. Ada materi kuliah yang ingin kamu tanyakan hari ini?";
        tampilkanPesan(pesanAwal, 'bot-message');
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