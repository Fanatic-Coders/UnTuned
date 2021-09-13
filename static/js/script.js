
// Confirm Password Validation for Register page
const check = function() {
    if (document.getElementById('password').value ==
      document.getElementById('cpassword').value) {
      document.getElementById('message').style.color = 'green';
      document.getElementById('message').innerHTML = ' ';
    } else {
      document.getElementById('message').style.color = 'red';
      document.getElementById('message').innerHTML = 'Password and confirm password should be same!';
    }
  }


const passIdtoModal = function(id, name, desc, price, imgid) {

  document.getElementById('productModalLabel').innerText = name;
  document.getElementById('prodDesc').innerText = desc;
  document.getElementById('prodPrice').innerText = price;

  // Selecting modal form
  form = document.getElementById('modalform');
  form.setAttribute('action', `/add_to_cart/${id}`);

  // Selecting img tag in modal
  img = document.getElementById('modalimg');
  img.setAttribute('src', `/getImg/${imgid}`);
  console.log(imgid);

  console.log(img);
}


