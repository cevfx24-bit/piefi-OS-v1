include $(TOPDIR)/rules.mk
PKG_NAME:=piefi-branding
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
include $(INCLUDE_DIR)/package.mk

define Package/piefi-branding
  SECTION:=base
  CATEGORY:=Base system
  TITLE:=pieFI OS Branding
  DEPENDS:=+luci-base
endef

define Package/piefi-branding/install
	$(INSTALL_DIR) $(1)/etc
	$(INSTALL_DATA) ./files/etc/banner $(1)/etc/banner
	$(INSTALL_DATA) ./files/etc/openwrt_release $(1)/etc/openwrt_release
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/etc/init.d/boot-piefi $(1)/etc/init.d/boot-piefi
	$(INSTALL_DIR) $(1)/etc/uci-defaults
	$(INSTALL_BIN) ./files/etc/uci-defaults/99-piefi $(1)/etc/uci-defaults/
	$(INSTALL_DIR) $(1)/www/luci-static/piefi
	$(CP) ./files/www/luci-static/piefi/* $(1)/www/luci-static/piefi/
endef

$(eval $(call BuildPackage,piefi-branding))
