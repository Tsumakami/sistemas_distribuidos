class Product():
    productId: str
    skuId: str
    displayName: str
    listPrice: float
    salePrice: float
    productName: str
    availableStock: int
    interStateAvailableStock: int

    def __init__(self, productId, skuId, displayName, 
        listPrice, salePrice, productName, availableStock, interStateAvailableStock):
        self.productId = productId
        self.skuId = skuId
        self.displayName = displayName
        self.listPrice = listPrice
        self.salePrice = salePrice
        self.productName = productName
        self.availableStock = availableStock
        self.interStateAvailableStock = interStateAvailableStock
   
