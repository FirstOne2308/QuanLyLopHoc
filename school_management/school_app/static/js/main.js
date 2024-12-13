const menu = document.querySelector('#sidebar');
const menuLinks = document.querySelector('.sidebar');
const main = document.querySelector('.list-container');

// Display Mobile Menu
const mobileMenu = () => {
  menu.classList.toggle('is-active');
  menuLinks.classList.toggle('active');
  main.classList.toggle('active');
}

menu.addEventListener('click', mobileMenu)



const dropdownMenu = document.querySelector(".dropdown-menu");
const dropdownButton = document.querySelector(".dropdown-button");

if (dropdownButton) {
    dropdownButton.addEventListener("click", () => {
    dropdownMenu.classList.toggle('show');
  });
}



const sidebarLink = document.querySelector(".sidebar-link");

const sidebarLinkSelect = () => {
  sidebarLink.classList.toggle('is-selected');
  // console.assert('hi');
}

sidebarLink.addEventListener('click', sidebarLinkSelect);


const mainRpSj = document.querySelector(".main-rp-sj");
const mainRpTerm = document.querySelector(".main-rp-term");


const tapTerm = document.querySelector(".item-term");
const tapSubject = document.querySelector(".item-subject");

tapTerm.addEventListener("click", () => {
  mainRpTerm.classList.remove("notactive");
  mainRpSj.classList.remove("active");
  tapTerm.classList.remove("notactive");
  tapSubject.classList.remove("active");
  
  mainRpTerm.classList.add("active");
  mainRpSj.classList.add("notactive");
  tapTerm.classList.add("active");
  tapSubject.classList.add("notactive");
});

tapSubject.addEventListener("click", () => {

  mainRpTerm.classList.remove("active");
  mainRpSj.classList.remove("notactive");
  tapSubject.classList.remove("notactive");
  tapTerm.classList.remove("active");

  mainRpTerm.classList.add("notactive");
  mainRpSj.classList.add("active");
  tapSubject.classList.add("active");
  tapTerm.classList.add("notactive");
})


// Lấy các phần tử modal và các nút điều khiển
const modal = document.getElementById('add-student-modal');
const addStudentBtn = document.getElementById('add-student-btn');
const closeModalBtn = document.getElementById('close-modal-btn');

// Khi người dùng nhấn nút "Thêm học sinh mới"
addStudentBtn.onclick = function() {
  modal.style.display = 'block'; // Hiển thị modal
}

// Khi người dùng nhấn vào nút đóng (×)
closeModalBtn.onclick = function() {
  modal.style.display = 'none'; // Ẩn modal
}

// Khi người dùng nhấn vào bất kỳ đâu ngoài modal, đóng modal
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = 'none';
  }
}
