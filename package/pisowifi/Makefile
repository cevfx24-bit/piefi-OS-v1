include $(TOPDIR)/rules.mk
PKG_NAME:=pisowifi
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
include $(INCLUDE_DIR)/package.mk

define Package/pisowifi
  SECTION:=net
  CATEGORY:=Network
  TITLE:=pieFI PisoWiFi System
  DEPENDS:=+python3-light +python3-flask +python3-yaml +python3-pyserial \
           +python3-sqlite3 +nginx-ssl +nftables +ip-full +kmod-usb-serial
endef

define Package/pisowifi/description
  pieFI OS PisoWiFi captive portal at coin daemon.
endef

define Build/Compile
endef

define Package/pisowifi/install
	$(INSTALL_DIR) $(1)/opt/pisowifi
	$(CP) ./files/* $(1)/opt/pisowifi/
	$(INSTALL_DIR) $(1)/etc/pisowifi
	$(INSTALL_CONF) ./files/config.yaml $(1)/etc/pisowifi/config.yaml
	$(INSTALL_DIR) $(1)/etc/nftables.d
	$(INSTALL_DATA) ./files/nftables/pisowifi.nft $(1)/etc/nftables.d/
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) $(1)/opt/pisowifi/pisowifi.init $(1)/etc/init.d/pisowifi
	$(INSTALL_DIR) $(1)/etc/uci-defaults
	$(INSTALL_BIN) $(1)/opt/pisowifi/firstboot.sh $(1)/etc/uci-defaults/99-piefi-pisowifi
endef

$(eval $(call BuildPackage,pisowifi))
