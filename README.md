# Specifications

### Expectations
- [x] The admin can assign users to the manager group

- [x] You can access the manager group with an admin token

- [ ] The admin can add menu items 

- [x] The admin can add categories

- [x] Managers can log in 

- [ ] Managers can update the item of the day

- [x] Managers can assign users to the delivery crew

- [ ] Managers can assign orders to the delivery crew

- [ ] The delivery crew can access orders assigned to them

- [ ] The delivery crew can update an order as delivered

- [x] Customers can register

- [x] Customers can log in using their username and password and get access tokens

- [x] Customers can browse all categories 

- [ ] Customers can browse all the menu items at once

- [ ] Customers can browse menu items by category

- [ ] Customers can paginate menu items

- [ ] Customers can sort menu items by price

- [ ] Customers can add menu items to the cart

- [ ] Customers can access previously added items in the cart

- [ ] Customers can place orders

- [ ] Customers can browse their own orders

### Base URL: `/api`

### Note
- User token is required for all features of the API with the exception of registering and viewing the menu

### User registration and token generation endpoints

`/users`
- GET
    - Anonymous: `401 Forbidden`
    - Admin: Retrieves all users information
    - Other authenticated users: Retrieves requesting user information
- POST
    - No role required: Registers a new user
    - Body:
        - username
        - password
        - email

`/users/me`
- GET
    - All authenticated users: Displays only the current user information

`/token/login`
- POST
    - Generates access tokens that can be used in other API calls
    - Body:
        - username
        - password

---

### User group management endpoints

`/groups/manager/users`
- GET
    - Manager: Returns all managers
- POST
    - Manager: `201 Created` Assigns the user in the payload to the manager group

`/groups/manager/users/{userId}`
- DELETE
    - Manager:
        - `200 OK` if deletion is okay
        - `404 Not found` if user is not found

`/groups/delivery-crew/users`
- GET
    - Manager: Returns all delivery crew members
- POST
    - Manager: `201 Created` Assigns the user in the payload to delivery crew group
    - Body:
        - username

`/groups/delivery-crew/users/{userId}`
- DELETE
    - Manager:
        - `200 OK` removes user from delivery crew
        - `404 Not found` if user is not found

---

### Categories endpoints

`categories`
- GET
    - All authenticated users: `200 Ok` Lists all categories
- POST
    - Admin: `201 Created` Creates a new category item
    - Body:
        - title

---

### Menu-items endpoints

`menu-items`
- GET
    - Customer, Delivery Crew, Manager: `200 Ok` Lists all menu items
- POST
    - Customer, Delivery Crew: `403 Unauthorized`
    - Manager: `201 Created` Creates a new menu item

`menu-items/{menuItem}`
- GET
    - Customer, Delivery Crew, Manager: `200 OK` Lists single menu item
- PUT, PATCH, DELETE
    - Customer, Delivery Crew: `403 Unauthorized`
    - Manager: Updates or deletes single menu item
---

### Cart management endpoints

`/cart/menu-items`
- GET
    - Customer: Returns current items in the cart for the current user token
- POST
    - Customer: Adds the menu item to the cart. Sets the authenticated user as the user id for these cart items
- DELETE
    - Customer: Deletes all menu items created by the current user token

---

### Order management endpoints

`/orders`
- GET
    - Customer: Returns all orders with order items created by this user
    - Managers: Returns all orders with order items by all users
    - Delivery Crew: Returns all orders with order items assigned to the delivery crew
- POST
    - Customer: Creates a new order item for the current user. Gets current cart items from the cart endpoints and adds those items to the order items table. Then deletes all items from the cart for this user.
    - Managers: 

`/orders/{orderId}`
- GET
    - Customer: Returns all items for this order id. If the order ID doesn’t belong to the current user, it displays an appropriate HTTP error status code
- PUT, PATCH
    - Delivery Crew: A delivery crew can use this endpoint to update the order status to 0 or 1. The delivery crew will not be able to update anything else in this order.
- DELETE
    - Manager: Deletes this order
