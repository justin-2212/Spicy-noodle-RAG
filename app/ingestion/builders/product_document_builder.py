"""Product document builder for RAG ingestion."""

from typing import List, Dict, Any
from app.utils.logger import logger


class ProductDocumentBuilder:
    """Convert product data into RAG-ready documents."""

    @staticmethod
    def build_document(product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a product data dictionary into a RAG document.

        Args:
            product_data: Product data dictionary from loader

        Returns:
            RAG-ready document with text and metadata
        """
        try:
            lines = []

            # Product name
            lines.append(f"Tên món ăn: {product_data['name']}")

            # Category
            if product_data['category']:
                lines.append(
                    f"Loại món: {product_data['category']['name']}"
                )

            # Price
            lines.append(
                f"Giá bán: {product_data['price']:,.0f} VNĐ"
            )

            # Spicy level
            if product_data['max_spicy_level'] > 0:
                lines.append(
                    f"Cấp độ cay: Có thể chọn từ cấp 0 đến cấp {product_data['max_spicy_level']}"
                )
            else:
                lines.append("Cấp độ cay: Không cay")

            # Description
            if product_data['short_description']:
                lines.append(
                    f"Mô tả chi tiết: {product_data['short_description']}"
                )

            # Stock
            stock_status = (
                "Đang còn hàng phục vụ"
                if product_data['stock_quantity'] > 0
                else "Hiện đang hết hàng"
            )

            lines.append(
                f"Tình trạng phục vụ: {stock_status} "
                f"(Số lượng còn lại: {product_data['stock_quantity']} phần)"
            )

            # Best seller
            if product_data['is_best_seller']:
                lines.append("Đây là món ăn bán chạy nhất (Best Seller) của quán.")

            # Combo components
            if product_data.get('combo_components'):
                if product_data.get('is_combo'):
                    lines.append("Thành phần trong combo bao gồm:")
                else:
                    lines.append("Nguyên liệu chính của món:")
                comp_lines = [
                    f"  - {comp['name']} (Số lượng: {comp['quantity']})"
                    for comp in product_data['combo_components']
                ]
                lines.extend(comp_lines)

            # Rating
            if product_data['average_rating']:
                lines.append(
                    f"Đánh giá khách hàng: "
                    f"{product_data['average_rating']:.1f} trên 5 sao "
                    f"dựa trên {product_data['rating_count']} lượt bình chọn."
                )

            # Toppings
            if product_data['toppings']:
                topping_info = [
                    f"{topping['name']} (giá {topping['price']:,.0f} VNĐ)"
                    for topping in product_data['toppings']
                ]

                lines.append(
                    f"Các loại Topping có thể thêm: {', '.join(topping_info)}"
                )

            # Reviews
            if product_data['reviews']:
                lines.append("Nhận xét và phản hồi từ khách hàng thực tế:")

                for i, review in enumerate(
                    product_data['reviews'][:5],
                    1
                ):
                    lines.append(
                        f"  + Nhận xét {i}: ({review['rating']}/5 sao) \"{review['comment']}\""
                    )

                if len(product_data['reviews']) > 5:
                    lines.append(
                        f"Ngoài ra còn có {len(product_data['reviews']) - 5} "
                        f"lượt nhận xét tích cực khác từ khách hàng."
                    )

            # Final text
            full_text = "\n".join(lines)

            # Metadata
            metadata = {
                "product_id": product_data["id"],
                "product_name": product_data["name"],
                "category": (
                    product_data["category"]["name"]
                    if product_data["category"]
                    else "Unknown"
                ),
                "price": float(product_data["price"]),
                "max_spicy_level": product_data["max_spicy_level"],
                "is_combo": product_data["is_combo"],
                "is_best_seller": product_data["is_best_seller"],
                "average_rating": (
                    float(product_data["average_rating"])
                    if product_data["average_rating"]
                    else 0.0
                ),
                "rating_count": product_data["rating_count"],
                "stock_quantity": product_data["stock_quantity"],
                "has_reviews": len(product_data["reviews"]) > 0,
                "review_count": len(product_data["reviews"]),
                "topping_count": len(product_data["toppings"]),
            }

            return {
                "id": product_data["id"],
                "text": full_text,
                "metadata": metadata,
            }

        except Exception as e:
            logger.error(
                f"Failed to build document for product "
                f"{product_data.get('id')}: {str(e)}"
            )
            raise

    @staticmethod
    def build_documents_batch(
        products_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert multiple products into RAG documents.
        """
        logger.info(
            f"Building {len(products_data)} documents..."
        )

        documents = []
        errors = []

        for product_data in products_data:
            try:
                document = (
                    ProductDocumentBuilder.build_document(
                        product_data
                    )
                )

                documents.append(document)

            except Exception as e:
                error_msg = (
                    f"Product "
                    f"{product_data.get('id', 'unknown')}: "
                    f"{str(e)}"
                )

                errors.append(error_msg)

                logger.error(error_msg)

        if errors:
            logger.warning(
                f"Failed to build {len(errors)} documents"
            )

        logger.info(
            f"Built {len(documents)} documents successfully"
        )

        return documents

    @staticmethod
    def get_document_stats(
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate statistics about documents.
        """
        if not documents:
            return {
                "total_documents": 0,
                "avg_text_length": 0,
                "avg_rating": 0,
                "total_reviews": 0,
                "combos": 0,
                "best_sellers": 0,
            }

        total_text_length = sum(
            len(doc["text"])
            for doc in documents
        )

        total_reviews = sum(
            doc["metadata"]["review_count"]
            for doc in documents
        )

        combos = sum(
            1
            for doc in documents
            if doc["metadata"]["is_combo"]
        )

        best_sellers = sum(
            1
            for doc in documents
            if doc["metadata"]["is_best_seller"]
        )

        avg_rating = (
            sum(
                doc["metadata"]["average_rating"]
                for doc in documents
            )
            / len(documents)
        )

        return {
            "total_documents": len(documents),
            "avg_text_length": (
                total_text_length // len(documents)
            ),
            "avg_rating": round(avg_rating, 2),
            "total_reviews": total_reviews,
            "combos": combos,
            "best_sellers": best_sellers,
        }

    @staticmethod
    def build_topping_summary_document(toppings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a summary document for all available toppings.
        """
        if not toppings_data:
            return None

        lines = [
            "ĐÂY LÀ DANH SÁCH ĐẦY ĐỦ VÀ CHÍNH XÁC NHẤT CÁC LOẠI TOPPING CỦA QUÁN (CẬP NHẬT MỚI NHẤT):",
            "Vui lòng liệt kê toàn bộ danh sách này nếu khách hàng hỏi về các loại topping hiện có.",
            ""
        ]
        
        for topping in toppings_data:
            lines.append(f"* {topping['name']}: {topping['price']:,.0f} VNĐ")
            
        lines.append("\nLưu ý: Khách hàng có thể gọi thêm các loại topping này khi đặt bất kỳ món mì cay nào.")
        
        return {
            "id": 99999, # Special ID for topping summary
            "text": "\n".join(lines),
            "metadata": {
                "product_id": 99999,
                "product_name": "Danh sách Topping Đầy Đủ",
                "category": "Topping Summary",
                "is_summary": True,
                "type": "topping_list"
            }
        }

    @staticmethod
    def build_menu_summary_document(products_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a summary document for the entire menu.
        """
        if not products_data:
            return None

        lines = [
            "DANH SÁCH TOÀN BỘ THỰC ĐƠN (MENU) CHÍNH THỨC CỦA QUÁN:",
            "Vui lòng liệt kê toàn bộ các món trong nhóm nếu khách hàng hỏi về menu.",
            ""
        ]
        
        # Group by category
        categories = {}
        for product in products_data:
            cat_name = product['category']['name'] if product['category'] else "Món khác"
            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(product)
            
        for cat_name, products in categories.items():
            lines.append(f"Nhóm món: {cat_name.upper()}")
            for p in products:
                lines.append(f"  - {p['name']}: {p['price']:,.0f} VNĐ")
            lines.append("") # Spacing between categories
                
        return {
            "id": 88888, # Special ID for menu summary
            "text": "\n".join(lines),
            "metadata": {
                "product_id": 88888,
                "product_name": "Toàn bộ thực đơn (Menu Summary)",
                "category": "Menu Summary",
                "is_summary": True,
                "type": "menu_list"
            }
        }