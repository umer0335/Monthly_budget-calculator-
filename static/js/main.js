document.addEventListener("DOMContentLoaded", () => {
  const monthPicker = document.querySelector("#month-picker");
  if (monthPicker) {
    monthPicker.addEventListener("change", () => {
      monthPicker.form?.submit();
    });
  }

  const currencyInputs = document.querySelectorAll('input[data-money="true"]');
  currencyInputs.forEach((input) => {
    input.addEventListener("blur", () => {
      const parsed = Number.parseFloat(input.value);
      input.value = Number.isFinite(parsed) ? parsed.toFixed(2) : "0.00";
    });
  });

  const revealItems = document.querySelectorAll(
    ".stat-card, .budget-panel, .save-banner"
  );
  revealItems.forEach((item, index) => {
    item.animate(
      [
        { opacity: 0, transform: "translateY(8px)" },
        { opacity: 1, transform: "translateY(0)" },
      ],
      {
        duration: 320,
        delay: index * 28,
        fill: "both",
        easing: "ease-out",
      }
    );
  });
});
