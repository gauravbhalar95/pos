let d = document.getElementById("import")
if (d) { 
d.addEventListener("click", function () {
  let exists = document.getElementById("form")
  if (exists){
    return;
  }else{
  let form = document.createElement("form");
  form.method = "POST";
  form.id = "form";
  form.enctype = "multipart/form-data";
  form.action = "/inventory/submit";
  let o = document.createElement("input");
  o.type = "file";
  o.name = "file";
  o.className = "im";
  let submit = document.createElement("button");
  submit.type = "submit";
  submit.className = "submit";
  submit.innerText = "submit";
  let down = document.createElement("button");
  down.type = "button";
  down.innerText = "template";
  down.className = "download";
  down.onclick;
  down.addEventListener("click", function () {
    window.location.href = "/get-template"
  })

  let but = document.createElement("button");
  but.type = "button";
  but.innerText = "x";
  but.className = "but";
  but.onclick;
  but.addEventListener("click", function () {
    form.remove();
  });
  form.appendChild(submit);
  form.appendChild(o);
  form.appendChild(but);
  form.appendChild(down);
  document.body.appendChild(form);
}

})}


function show(){
  let showpassword = document.getElementById("pass")
  let number = document.getElementById("pin")
  if (showpassword.type == "password" || number.type == "password"){
    showpassword.type = "text";
    number.type = "pin"
  }
  else{
    showpassword.type = "password";
    number.type = "password"
  } 
}
// 🛒 Cart
let cart = [];



// 💰 GST (global)
//let GST = 0;

// 📦 Load GST once
//function loadGST() {
//  fetch("/get-gst")
 //   .then(res => res.json())
//    .then(data => {
//      GST = data.gst / 100;
 //     console.log("GST Loaded:", GST);
//    })
  //  .catch(err => console.error("Error fetching GST:", err));
//}

// ➕ Add to Cart
function addToCart(name, price, barcode, gst) {

  price = parseFloat(price);

  let found = cart.find(item => item.name === name);

  if (found) {
    found.qty++;
    found.total = found.qty * found.price;
  } else {
    cart.push({ name: name, price: price, barcode: barcode, qty: 1,gst: gst, total: price});
  }

  renderCart();
}

// 🔁 Render Cart
function renderCart() {


  
  let table = document.getElementById("carttable");

  table.innerHTML = `
    <tr>
      <th>Id</th>
      <th>Product Name</th>
      <th>Barcode</th>
      <th>Qty</th>
      <th>Rate</th>
      <th>Amount</th>
        <th>Gst</th>
      <th>Action</th>
    </tr>
  `;

  let total = 0;

  cart.forEach((item, i) => {

    total += item.total;

   let tbody = table.querySelector("tbody");
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
      <td>${item.total.toFixed(2)}</td>
        <td>${item.gst.toFixed(2)}</td>
      <td><button onclick="removeItem(${i})">X</button></td>
    `;
  });

  updateTotal(total);
}

// ➕ Increase Qty
function increaseQty(i) {
  cart[i].qty++;
  cart[i].total = cart[i].qty * cart[i].price;
  renderCart();
}

// ➖ Decrease Qty
function decreaseQty(i) {
  if (cart[i].qty > 1) {
    cart[i].qty--;
    cart[i].total = cart[i].qty * cart[i].price;
  } else {
    cart.splice(i, 1);
  }
  renderCart();
}

// ❌ Remove Item
function removeItem(i) {
  cart.splice(i, 1);
  renderCart();
}

// 💰 Update Total
function updateTotal(total) {

  total = parseFloat(total) || 0;
  let gstRate = parseFloat(item.gst) || 0;

  let GST = +(total * gstRate).toFixed(2);
  let grand = +(total + GST).toFixed(2);

  document.getElementById("total").innerText = total.toFixed(2);
  document.getElementById("gst").innerText = GST.toFixed(2);
  document.getElementById("grand").innerText = grand.toFixed(2);
}

// 📱 Barcode Scan
function handleScan(e) {

  if (e.key === "Enter") {

    let code = document.getElementById("scanner").value;

    fetch("/get-product/" + code)
      .then(res => res.json())
      .then(data => {

        if (!data.error) {
          addToCart(data.name, data.price, code);
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

  console.log("Sending data:", data);

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
  loadGST();
};