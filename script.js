const addForm = document.querySelector("#add-form");
const editForm = document.querySelector("#edit-form");
const editDialog = document.querySelector("#edit-dialog");
const expenseRows = document.querySelector("#expense-rows");
const emptyState = document.querySelector("#empty-state");
const formMessage = document.querySelector("#form-message");
const editMessage = document.querySelector("#edit-message");
const listMessage = document.querySelector("#list-message");
const searchForm = document.querySelector("#search-form");
const searchInput = document.querySelector("#search-input");
const resetSearchButton = document.querySelector("#reset-search");

document.querySelector("#today-label").textContent =
    new Intl.DateTimeFormat(undefined, {
        weekday: "short",
        month: "short",
        day: "numeric",
        year: "numeric",
    }).format(new Date());
document.querySelector("#expense-date").value =
    localDateString();

function localDateString() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

let currentExpenses = [];

function showMessage(element, message, isError = false) {
    element.textContent = message;
    element.classList.toggle("error", isError);
}

async function request(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    });
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.error || "The request could not be completed.");
    }
    return result;
}

function makeCell(text, className) {
    const cell = document.createElement("td");
    cell.textContent = text;
    if (className) {
        cell.className = className;
    }
    return cell;
}

function renderExpenses(expenses) {
    currentExpenses = expenses;
    expenseRows.replaceChildren();

    for (const expense of expenses) {
        const row = document.createElement("tr");
        row.append(
            makeCell(expense.expense_name, "expense-name-cell"),
        );

        const categoryCell = document.createElement("td");
        const category = document.createElement("span");
        category.className = "category-chip";
        category.textContent = expense.category;
        categoryCell.append(category);
        row.append(categoryCell);

        row.append(makeCell(expense.expense_date));
        row.append(makeCell(Number(expense.amount).toFixed(2), "amount-cell"));

        const actionsCell = document.createElement("td");
        const actions = document.createElement("div");
        actions.className = "row-actions";

        const editButton = document.createElement("button");
        editButton.className = "action-button";
        editButton.type = "button";
        editButton.textContent = "Edit";
        editButton.setAttribute("aria-label", `Edit ${expense.expense_name}`);
        editButton.addEventListener("click", () => openEditForm(expense));

        const deleteButton = document.createElement("button");
        deleteButton.className = "action-button delete";
        deleteButton.type = "button";
        deleteButton.textContent = "Delete";
        deleteButton.setAttribute(
            "aria-label",
            `Delete ${expense.expense_name}`,
        );
        deleteButton.addEventListener("click", () => deleteExpense(expense));

        actions.append(editButton, deleteButton);
        actionsCell.append(actions);
        row.append(actionsCell);
        expenseRows.append(row);
    }

    emptyState.hidden = expenses.length > 0;
    document.querySelector("#expense-count").textContent =
        String(expenses.length);
}

async function loadExpenses(search = "") {
    showMessage(listMessage, "");
    const query = search ? `?search=${encodeURIComponent(search)}` : "";
    try {
        const result = await request(`/api/expenses${query}`);
        renderExpenses(result.expenses);
        document.querySelector("#total-amount").textContent =
            Number(result.total).toFixed(2);
    } catch (error) {
        showMessage(listMessage, error.message, true);
        renderExpenses([]);
    }
}

function getFormData(form) {
    const values = new FormData(form);
    return {
        expense_name: values.get("expense_name").trim(),
        amount: Number(values.get("amount")),
        category: values.get("category").trim(),
        expense_date: values.get("expense_date"),
    };
}

addForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    showMessage(formMessage, "");
    try {
        await request("/api/expenses", {
            method: "POST",
            body: JSON.stringify(getFormData(addForm)),
        });
        addForm.reset();
        document.querySelector("#expense-date").value =
            localDateString();
        showMessage(formMessage, "Expense added.");
        searchInput.value = "";
        resetSearchButton.hidden = true;
        await loadExpenses();
    } catch (error) {
        showMessage(formMessage, error.message, true);
    }
});

searchForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const search = searchInput.value.trim();
    resetSearchButton.hidden = !search;
    await loadExpenses(search);
});

resetSearchButton.addEventListener("click", async () => {
    searchInput.value = "";
    resetSearchButton.hidden = true;
    await loadExpenses();
});

function openEditForm(expense) {
    document.querySelector("#edit-id").value = expense.expense_id;
    document.querySelector("#edit-name").value = expense.expense_name;
    document.querySelector("#edit-amount").value = expense.amount;
    document.querySelector("#edit-category").value = expense.category;
    document.querySelector("#edit-date").value = expense.expense_date;
    showMessage(editMessage, "");
    editDialog.showModal();
}

editForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    showMessage(editMessage, "");
    const expenseId = document.querySelector("#edit-id").value;
    try {
        await request(`/api/expenses/${expenseId}`, {
            method: "PUT",
            body: JSON.stringify(getFormData(editForm)),
        });
        editDialog.close();
        showMessage(listMessage, "Expense updated.");
        await loadExpenses(searchInput.value.trim());
    } catch (error) {
        showMessage(editMessage, error.message, true);
    }
});

document.querySelector("#close-dialog").addEventListener("click", () => {
    editDialog.close();
});

async function deleteExpense(expense) {
    if (!window.confirm(`Delete "${expense.expense_name}"?`)) {
        return;
    }

    try {
        await request(`/api/expenses/${expense.expense_id}`, {
            method: "DELETE",
        });
        showMessage(listMessage, "Expense deleted.");
        await loadExpenses(searchInput.value.trim());
    } catch (error) {
        showMessage(listMessage, error.message, true);
    }
}

loadExpenses();
