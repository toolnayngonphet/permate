console.log("Super Data Filler content script loaded.");

const fieldMappings = {
    // ---- Lần 1 ----
    ten: "#__BVID__37",
    ho: "#__BVID__40",
    sdt: "#__BVID__46",
    matKhau: "#__BVID__49",
    nhapLaiMatKhau: "#__BVID__53"
    // ---- Lần 2 (sẽ thêm sau) ----
    // diaChi: "selector_cua_o_dia_chi",
};

function fillField(selector, value) {
    if (!selector) {
        console.warn("Selector rỗng, bỏ qua.");
        return;
    }
    try {
        const element = document.querySelector(selector);
        if (element) {
            element.value = value;
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            console.log(`✅ Đã điền "${value}" vào element: ${selector}`);
        } else {
            console.warn(`❌ Không tìm thấy element với selector: ${selector}`);
        }
    } catch (e) {
        console.error(`Lỗi khi điền vào selector "${selector}":`, e);
    }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "FILL_BY_STEP") {
        console.log(`Nhận lệnh điền cho Bước ${message.step}`, message.data);

        if (message.step === 1) {
            fillField(fieldMappings.ten, message.data.ten);
            fillField(fieldMappings.ho, message.data.ho);
            fillField(fieldMappings.sdt, message.data.sdt);
            fillField(fieldMappings.matKhau, message.data.password);
            fillField(fieldMappings.nhapLaiMatKhau, message.data.password);
        }

        sendResponse({ status: `Điền bước ${message.step} thành công!` });
        return true;
    }

    if (message.type === "SOLVE_CAPTCHA") {
        const recaptchaField = document.getElementById("g-recaptcha-response");
        if (recaptchaField) {
            recaptchaField.innerHTML = message.token;
            console.log("✅ Token captcha đã được điền.");
        } else {
            console.warn("❌ Không tìm thấy thẻ #g-recaptcha-response trên trang.");
        }
        sendResponse({ status: "Điền captcha thành công!" });
        return true;
    }
});