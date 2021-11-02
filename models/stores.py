from .product import Product
class Stores(Product):
    cdsWithStock: str

    def __init__(self, productId, skuId, displayName,
        listPrice, salePrice, productName, availableStock, interStateAvailableStock,
        cdsWithStock):
        super().__init__(productId, skuId, displayName,
            listPrice, salePrice, productName, availableStock, interStateAvailableStock,
            cdsWithStock)
        self.cdsWithStock = cdsWithStock
