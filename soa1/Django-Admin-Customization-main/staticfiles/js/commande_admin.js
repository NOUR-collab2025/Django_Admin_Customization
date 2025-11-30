var style = document.createElement('style');
style.innerHTML = `
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin:0; }
input[type=number] { -moz-appearance: textfield; }
`;
document.head.appendChild(style);

(function() {
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll('input[id$="prix"]').forEach(input => {
            // prevent user typing
            input.addEventListener('keydown', e => e.preventDefault());
            // optional: prevent pasting
            input.addEventListener('paste', e => e.preventDefault());
            // optional: prevent drop
            input.addEventListener('drop', e => e.preventDefault());
        });
        // Met à jour le total de la commande
        function updateTotal() {
            let rows = document.querySelectorAll('.dynamic-articlecommande_set');
            let total = 0;

            rows.forEach(row => {
                let qtyField = row.querySelector('input[id$="quantite"]');
                let priceField = row.querySelector('input[id$="prix"]');
                let productSelect = row.querySelector('select[id$="produit"]');

                // si le row n'a pas encore de unitPrice, on le récupère
                if (productSelect && !row.dataset.unitPrice && productSelect.value) {
                    fetchUnitPrice(row, productSelect.value);
                }

                if (qtyField && priceField) {
                    let qty = parseInt(qtyField.value || 0);
                    let unitPrice = parseFloat(row.dataset.unitPrice || 0);
                    let lineTotal = qty * unitPrice;
                    priceField.value = lineTotal.toFixed(2);
                    total += lineTotal;
                }
            });

            let totalField = document.querySelector('#id_prix_total');
            if (totalField) {
                totalField.value = total.toFixed(2);  // ✅ update the total input
                totalField.readOnly = true;
                totalField.style.pointerEvents = "none";
            }

        }

        // Récupère le prix unitaire depuis la DB
        function fetchUnitPrice(row, productId) {
            fetch('/get-produit-prix/' + productId + '/')
                .then(res => res.json())
                .then(data => {
                    row.dataset.unitPrice = parseFloat(data.prix) || 0;
                    updateTotal();
                });
        }

        // Événements avec delegation
        document.body.addEventListener('change', function(e) {
            let row = e.target.closest('.dynamic-articlecommande_set');
            if (!row) return;

            if (e.target.id.includes('produit')) {
                let productId = e.target.value;
                if (productId) {
                    fetchUnitPrice(row, productId);
                } else {
                    row.dataset.unitPrice = 0;
                    updateTotal();
                }
            }
        });

        document.body.addEventListener('input', function(e) {
            if (e.target.id.includes('quantite')) {
                updateTotal();
            }
        });

        document.body.addEventListener('click', function(e) {
            if (e.target.classList.contains('add-row') || e.target.classList.contains('delete-row')) {
                setTimeout(updateTotal, 100); // slightly longer delay for dynamic row creation
            }
        });

        // Recalcul initial
        updateTotal();
    });
})();
