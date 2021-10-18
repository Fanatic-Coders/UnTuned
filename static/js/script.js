// Confirm Password Validation for Register page
const check = function () {
  if (
    document.getElementById("password").value ==
    document.getElementById("cpassword").value
  ) {
    document.getElementById("message").style.color = "green";
    document.getElementById("message").innerHTML = " ";
  } else {
    document.getElementById("message").style.color = "red";
    document.getElementById("message").innerHTML =
      "Password and confirm password should be same!";
  }
};

// Method to pass the values of product to the modal
const passIdtoModal = function (id, name, desc, price, imgid) {
  document.getElementById("productModalLabel").innerText = name;
  document.getElementById("prodDesc").innerText = desc;
  document.getElementById("prodPrice").innerText = price;

  // Selecting modal form
  form = document.getElementById("modalform");
  form.setAttribute("action", `/add_to_cart/${id}`);

  // Selecting img tag in modal
  img = document.getElementById("modalimg");
  img.setAttribute("src", `/getImg/${imgid}`);
  console.log(imgid);

  console.log(img);
};

// Method to search the product
const searchProducts = function(){
    let search = document.getElementById('searchItem');
    search.addEventListener('input', function(){
        let inputValue = search.value.toLowerCase();
        let items = document.getElementsByClassName('card');
        let title = document.getElementsByClassName('prod-title');
        let desc = document.getElementsByClassName('prod-desc');
        let arr;
        for(let i = 0; i < items.length; i++){
            if(title[i].innerText.includes(inputValue) || desc[i].innerText.includes(inputValue)){
                items[i].parentElement.parentElement.style.display = 'block';
            }
            else{
                items[i].parentElement.parentElement.style.display = 'none';
            }
        }
    })
}