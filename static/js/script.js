window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

//delete function
function deleteItem(categoryName){
  const deleteBtns = document.querySelectorAll(`.${categoryName}-delete-button`);
  for (let i = 0; i < deleteBtns.length; i++) {
    const btn = deleteBtns[i];
    btn.onclick = function (e) {
      const itemId = e.target.dataset['id'];
      const confirmation = confirm('Are you sure to delete?');
      if (confirmation) {
        fetch(`/${categoryName}s/${itemId}`, {
          method: 'DELETE',
        }).then(function () {
          const item = e.target.parentElement;
          const items = item.parentElement;
          item.remove();
          if (items.children.length === 0) {
            const areaTitle = items.parentElement.querySelector('.area-title');
            areaTitle.remove();
            items.remove();
          }
        });
      }
    };
  }
}
//venue delete on list page 
deleteItem('venue')
