from typing import Optional
from fastmcp import FastMCP


class PromptRegistry:
    """Register @mcp.prompt() functions with a FastMCP instance."""

    @staticmethod
    def register_prompts(mcp: FastMCP) -> None:  # type: ignore[type-arg]
        """Register all prompt functions."""

        @mcp.prompt()
        def product_recommendation_prompt(budget: float, category: Optional[str] = None) -> str:  # type: ignore[misc]
            """
            Prompt: Recommend best products within a budget.
            Args:
                budget: Available budget in default currency.
                category: Optional product category filter.
            """
            cat_txt = f" {category} kategorisindeki" if category else ""
            return (
                f"{cat_txt} ürünler arasından {budget:.2f} birim bütçe ile en iyi seçenekleri öner. "
                "Fiyat/performans, stok durumu ve popülerlik kriterlerini değerlendir."
            )

        @mcp.prompt()
        def inventory_overview_prompt(threshold: int = 10) -> str:  # type: ignore[misc]
            """Prompt: Analyse inventory health above/below threshold."""
            return (
                f"Stok analizi yap: {threshold} adetten düşük ürünleri vurgula, kritik stok uyarıları, "
                "kategori bazlı stok dağılımı ve finansal etkiyi açıkla."
            )

        @mcp.prompt()
        def executive_summary_prompt() -> str:  # type: ignore[misc]
            """Prompt: Create an executive summary of key business metrics."""
            return (
                "Yönetici özeti oluştur: toplam ürün adedi, envanter değeri, en çok kazandıran kategori, "
                "düşük stok uyarıları ve stratejik öneriler sun."
            ) 