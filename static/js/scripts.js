function print(sale_id){
    window.location.href = "/billing/<int:sale_id>"
}



// --- Authentication & UI Functions ---
function template() {
    window.location.href = "/get-template";
};

function buyPlan(plan) {
    window.location.href = "/buy_subscription/" + plan;
};
let currentpage = window.location.pathname;

if (currentpage !== "/login" && currentpage !== "/register"){ 
// Create Logout Button
let logout = document.createElement("button");
logout.type = "button"; // Changed from submit to button
logout.innerText = "LogOut";
logout.className = "logout";
logout.addEventListener("click", function () {
    window.location.href = "/logout";
});
document.body.appendChild(logout)};

function new_form(){
    window.location.href = "/securty";

let  form = document.getElementById("fxr_form");

if (currentpage === "/register"){
        form.action = "/securty";
} else {
        form.action = "/forgetpassword";
    };
};
function show() {
    let showpassword = document.getElementById("pass");
    let number = document.getElementById("pin");
    if (showpassword && number) {
        let type = (showpassword.type === "password") ? "text" : "password";
        showpassword.type = type;
        number.type = type;
    }
}

function pdf(){
    window.location.href = "/print/${id}"
}





let cart = [];
let GST = 0;

function button_new(name){
fetch(`/get-gst/${name}`, {
    method: "GET"
})
        .then(response => response.json())
        .then(data => {
            console.log("gst",data);

        let name = data[1][0]
        let price = data[1][2]
        let barcode = data[1][3]
        let gst = data[1][1]

            addToCart(name,price,barcode,gst);
            handleScan(barcode,price,name,gst);

        })
        .catch(error => {
            console.log("error", error);
        });
    

    renderCart();
}



function addToCart(name, price, barcode, gst) {
    
    price = parseFloat(price);
    gst = parseFloat(gst);
    let found = cart.find(item => item.barcode === barcode);

    if (found) {
        found.qty++;
        found.total = found.qty * found.price;
    } else {
        cart.push({price, name, barcode, gst, qty: 1, total:price});
    };
    
}
function renderCart() {
    
    let table = document.getElementById("carttable");
    if (!table) return;

    table.innerHTML = `<thead><tr><th>Id</th><th>Product Name</th><th>Barcode</th><th>Qty</th><th>Rate</th><th>GST %</th><th>Amount</th><th>Action</th></tr></thead><tbody></tbody>`;
    let tbody = table.querySelector("tbody");
    let total = 0;

    cart.forEach((item, i) => {
        total += item.total;
        let row = tbody.insertRow();
        row.innerHTML = `
            <td>${i + 1}</td>
            <td>${item.name}</td>
            <td>${item.barcode}</td>
            <td>
                <button onclick="decreaseQty(${i})">-</button>
                ${item.qty}
                <button onclick="increaseQty(${i})">+</button>
            </td>
            <td>${item.price.toFixed(2)}</td>
            <td>${item.gst}%</td>
            <td>${item.total.toFixed(2)}</td>
            <td><button onclick="removeItem(${i})">X</button></td>`;
    });
    updateTotal(total);
}

function increaseQty(i) { cart[i].qty++; cart[i].total = cart[i].qty * cart[i].price; renderCart(); }
function decreaseQty(i) { 
    if (cart[i].qty > 1) { cart[i].qty--; cart[i].total = cart[i].qty * cart[i].price; } 
    else { cart.splice(i, 1); }
    renderCart(); 
}
function removeItem(i) { cart.splice(i, 1); renderCart(); }

function updateTotal(total) {
    let totalGST = 0;
    cart.forEach(item => { totalGST += (item.total * item.gst) / 100; });
    let grand = total + totalGST;

    if(document.getElementById("total")) document.getElementById("total").innerText = total.toFixed(2);
    if(document.getElementById("gst")) document.getElementById("gst").innerText = totalGST.toFixed(2);
    if(document.getElementById("grand")) document.getElementById("grand").innerText = grand.toFixed(2);
}

// --- Clock Logic ---
function initClock() {
    const clock = document.getElementById("clock");
    if (!clock) return;

    const roman = [
        "XII", "I", "II", "III", "IV", "V",
        "VI", "VII", "VIII", "IX", "X", "XI"
    ];

    roman.forEach((num, i) => {
        const el = document.createElement("div");
        el.className = "number";
        el.innerText = num;

        const angle = i * 30;
        const radius = 130;

        const x = 160 + radius * Math.sin(angle * Math.PI / 180);
        const y = 160 - radius * Math.cos(angle * Math.PI / 180);

        el.style.left = x + "px";
        el.style.top = y + "px";

        clock.appendChild(el);
    });

    updateClock();
};


function updateClock() {
    const now = new Date();
    const seconds = now.getSeconds() + now.getMilliseconds()/1000;
    const minutes = now.getMinutes() + seconds/60;
    const hours = now.getHours()%12 + minutes/60;

    const sEl = document.getElementById("second");
    const mEl = document.getElementById("minute");
    const hEl = document.getElementById("hour");

    if (sEl) sEl.style.transform = `rotate(${seconds * 6}deg)`;
    if (mEl) mEl.style.transform = `rotate(${minutes * 6}deg)`;
    if (hEl) hEl.style.transform = `rotate(${hours * 30}deg)`;

    requestAnimationFrame(updateClock);
};

// --- Main Init ---
document.addEventListener("DOMContentLoaded", () => {
    // Focus scanner
    const scanner = document.getElementById("scanner");
    if (scanner) scanner.focus()
    

    // Start Clock
    initClock();
});
// 📱 Barcode Scan
function handleScan(e) {
  if (e.key === "Enter") {
    let code = document.getElementById("scanner").value;

    fetch("/get-product/" + code)
      .then(res => res.json())
      .then(data => {
        if (!data.error) {
          addToCart(data.name, data.price, code, data.gst); // ✅ pass GST
        } else {
          alert("Product not found");
        }
        
        document.getElementById("scanner").value = "";
        document.getElementById("scanner").focus();
      })
      .catch(err => console.error("Scan Error:", err));
  }
}

// 💳 Checkout
function checkout() {
  let data = {
    items: cart,
    total: parseFloat(document.getElementById("total").innerText),
    gst: parseFloat(document.getElementById("gst").innerText),
    grand: parseFloat(document.getElementById("grand").innerText)
  };

  fetch("/save-bill", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(res => {
      alert(res.message);
      location.reload();
    })
    .catch(err => console.error("Checkout Error:", err));
}

// 🎯 On Load
window.onload = () => {
  document.getElementById("scanner").focus();
};