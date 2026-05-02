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
            lines.append(f"Tên món: {product_data['name']}")

            # Category
            if product_data['category']:
                lines.append(
                    f"Danh mục: {product_data['category']['name']}"
                )

            # Price
            lines.append(
                f"Giá: {product_data['price']:,.0f} VNĐ"
            )

            # Spicy level
            if product_data['max_spicy_level'] > 0:
                lines.append(
                    f"Độ cay tối đa: Cấp {product_data['max_spicy_level']}"
                )

            # Description
            if product_data['short_description']:
                lines.append(
                    f"Mô tả: {product_data['short_description']}"
                )

            # Stock
            stock_status = (
                "Còn hàng"
                if product_data['stock_quantity'] > 0
                else "Hết hàng"
            )

            lines.append(
                f"Tình trạng: {stock_status} "
                f"({product_data['stock_quantity']} sản phẩm)"
            )

            # Best seller
            if product_data['is_best_seller']:
                lines.append("Sản phẩm bán chạy")

            # Combo
            if product_data['is_combo']:
                lines.append("Sản phẩm combo")
                if product_data.get('combo_components'):
                    comp_lines = [
                        f"  + {comp['name']} (x{comp['quantity']})"
                        for comp in product_data['combo_components']
                    ]
                    lines.append("Thành phần combo:")
                    lines.extend(comp_lines)

            # Rating
            if product_data['average_rating']:
                lines.append(
                    f"Đánh giá: "
                    f"{product_data['average_rating']:.1f}/5.0 "
                    f"({product_data['rating_count']} lượt đánh giá)"
                )

            # Toppings
            if product_data['toppings']:
                topping_names = [
                    topping['name']
                    for topping in product_data['toppings']
                ]

                lines.append(
                    f"Topping có sẵn: {', '.join(topping_names)}"
                )

            # Reviews
            if product_data['reviews']:
                lines.append("Nhận xét khách hàng:")

                for i, review in enumerate(
                    product_data['reviews'][:5],
                    1
                ):
                    lines.append(
                        f"{i}. "
                        f"({review['rating']}/5) "
                        f"{review['comment']}"
                    )

                if len(product_data['reviews']) > 5:
                    lines.append(
                        f"Và {len(product_data['reviews']) - 5} "
                        f"nhận xét khác"
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