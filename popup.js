import { ds_ho } from './data/ho_vietnam.js';
import { ds_ten } from './data/ten_vietnam.js';
import { ds_bio } from './data/mo_ta_ve_ban.js';
import { ds_ads_desc } from './data/mo_ta_ads.js';
import { API_KEY_2CAPTCHA } from './config.js';

function saveData(dataObject) {
    chrome.storage.local.set({ savedData: dataObject }, () => {
        console.log("Dữ liệu đã được lưu.");
    });
}

function loadAndDisplayData() {
    chrome.storage.local.get(['savedData'], (result) => {
        if (result.savedData) {
            const data = result.savedData;
            for (const key in data) {
                const inputElement = document.getElementById(key);
                if (inputElement) {
                    inputElement.value = data[key];
                }
            }
        } else {
            generateAllData();
        }
    });
}

function choice(arr) {
    if (!arr || arr.length === 0) return "Chưa có dữ liệu";
    return arr[Math.floor(Math.random() * arr.length)];
}

function randint(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

const generateFunctions = {
    ho: () => choice(ds_ho),
    ten: () => choice(ds_ten),
    sdt: () => {
        const dau_so = ["32", "33", "34", "35", "36", "37", "38", "39", "70", "76", "77", "78", "79", "81", "82", "83", "84", "85"];
        return choice(dau_so) + Array.from({ length: 7 }, () => randint(0, 9)).join('');
    },
    password: () => {
        const lower = "abcdefghijklmnopqrstuvwxyz", upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", digits = "0123456789", special = "!@#$%^&*()-_=+[]{}|;:,.<>?/";
        const all = lower + upper + digits + special;
        let pass = [choice(lower), choice(upper), choice(digits), choice(special)];
        for (let i = 4; i < randint(10, 16); i++) { pass.push(choice(all)); }
        return pass.sort(() => 0.5 - Math.random()).join('');
    },
    bio: () => choice(ds_bio).replace(/^\d+\.\s*/, ''),
    ads_desc: () => choice(ds_ads_desc).replace(/^\d+\.\s*/, ''),
    visit: () => randint(50, 1000) * 10,
    username: async () => {
        try {
            const response = await fetch("https://tienichhay.net/ho-so-ngau-nhien.html");
            const text = await response.text();
            return text.split('Username</td>\n\t\t\t\t<td><strong>')[1].split('</strong></td>')[0];
        } catch { return "Lỗi khi lấy username"; }
    },
    address: async () => {
        try {
            const response = await fetch("https://tienichhay.net/ho-so-ngau-nhien.html");
            const text = await response.text();
            return text.split('Địa chỉ đầy đủ</td>\n\t\t\t<td><strong>')[1].split('</strong></td>')[0];
        } catch { return "Lỗi khi lấy địa chỉ"; }
    }
};

const fields = [
    { key: "ho", label: "Họ" }, { key: "ten", label: "Tên" },
    { key: "username", label: "Username" }, { key: "password", label: "Mật khẩu" },
    { key: "sdt", label: "SĐT" }, { key: "address", label: "Địa chỉ" },
    { key: "bio", label: "Giới thiệu" }, { key: "ads_desc", label: "Mô tả Ads" },
    { key: "visit", label: "Lượt truy cập" }
];

const dataFieldsContainer = document.getElementById('data-fields');
fields.forEach(({ key, label }) => {
    const row = document.createElement('div');
    row.className = 'row';
    row.innerHTML = `<label for="${key}">${label}</label><input type="text" id="${key}" readonly><button data-copy-target="${key}">Copy</button>`;
    dataFieldsContainer.appendChild(row);
});

async function generateAllData() {
    const generatedData = {};
    for (const field of fields) {
        const inputElement = document.getElementById(field.key);
        inputElement.value = "Đang tải...";
        const value = await generateFunctions[field.key]();
        inputElement.value = value;
        generatedData[field.key] = value;
    }
    saveData(generatedData);
}

function sendMessageToContentScript(message) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0] && tabs[0].id) {
            chrome.tabs.sendMessage(tabs[0].id, message, (response) => {
                if (chrome.runtime.lastError) {
                    console.warn("Lỗi khi gửi tin nhắn:", chrome.runtime.lastError.message);
                }
            });
        }
    });
}

const captchaStatus = document.getElementById('captchaStatus');
const SITE_KEY = "6LffITgpAAAAAMdr7L8asMGE0qitwVuLgS3xHYQp";

async function solveCaptcha() {
    if (!API_KEY_2CAPTCHA || API_KEY_2CAPTCHA === "KEY_CUA_BAN_O_DAY") {
        captchaStatus.textContent = "Vui lòng nhập API Key vào file config.js";
        return;
    }

    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const currentTab = tabs[0];
    if (!currentTab) {
        captchaStatus.textContent = "Không tìm thấy tab hiện tại.";
        return;
    }

    captchaStatus.textContent = "Đang gửi yêu cầu đến 2Captcha...";
    try {
        const res = await fetch(`http://2captcha.com/in.php?key=${API_KEY_2CAPTCHA}&method=userrecaptcha&googlekey=${SITE_KEY}&pageurl=${currentTab.url}&json=1`).then(r => r.json());
        if (res.status !== 1) throw new Error(res.request);

        const requestId = res.request;
        captchaStatus.textContent = `Đang đợi kết quả (ID: ${requestId})...`;

        for (let i = 0; i < 24; i++) {
            await new Promise(resolve => setTimeout(resolve, 5000));
            const check = await fetch(`http://2captcha.com/res.php?key=${API_KEY_2CAPTCHA}&action=get&id=${requestId}&json=1`).then(r => r.json());
            if (check.status === 1) {
                captchaStatus.textContent = "✅ Captcha đã giải xong!";
                sendMessageToContentScript({ type: "SOLVE_CAPTCHA", token: check.request });
                return;
            }
            captchaStatus.textContent += ".";
        }
        captchaStatus.textContent = "❌ Hết thời gian chờ captcha.";
    } catch (error) {
        captchaStatus.textContent = `❌ Lỗi: ${error.message}`;
    }
}

document.getElementById('solveCaptchaBtn').addEventListener('click', solveCaptcha);
document.getElementById('generateBtn').addEventListener('click', generateAllData);
dataFieldsContainer.addEventListener('click', (event) => {
    if (event.target.tagName === 'BUTTON' && event.target.dataset.copyTarget) {
        const targetId = event.target.dataset.copyTarget;
        const textToCopy = document.getElementById(targetId).value;
        navigator.clipboard.writeText(textToCopy).then(() => {
            const originalText = event.target.textContent;
            event.target.textContent = 'Copied!';
            setTimeout(() => { event.target.textContent = originalText; }, 1000);
        });
    }
});
document.addEventListener('DOMContentLoaded', loadAndDisplayData);

document.getElementById('fillStep1Btn').addEventListener('click', () => {
    const dataToSend = {};
    fields.forEach(({ key }) => {
        const inputElement = document.getElementById(key);
        if (inputElement) {
            dataToSend[key] = inputElement.value;
        }
    });
    if (!dataToSend.ten || dataToSend.ten === "Chưa có dữ liệu") {
        alert("Dữ liệu chưa sẵn sàng, vui lòng thử lại hoặc bấm 'Tạo Mới'!");
        return;
    }
    sendMessageToContentScript({
        type: "FILL_BY_STEP",
        step: 1,
        data: dataToSend
    });
});