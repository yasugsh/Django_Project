from django.db import transaction
import logging
from rest_framework import serializers

from goods.models import SKUSpecification, SKU, GoodsCategory, SPU, SpecificationOption, \
    SPUSpecification, Brand, GoodsChannel, GoodsChannelGroup, SKUImage
from project_admin.utils import get_fdfs_url


logger = logging.getLogger('django')


class SKUSpecificationSerializer(serializers.ModelSerializer):
    """SKU规格序列化器"""

    # 模型类默认自动构建关联表id字段，但序列化时不会自动映射此字段
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification  # 外键关联SKU表
        fields = ['spec_id', 'option_id']


class SKUSerializer(serializers.ModelSerializer):
    """SKU表信息的序列化器"""

    # SKU模型类默认自动构建关联表id字段，但序列化时不会自动映射此字段
    category_id = serializers.IntegerField()
    spu_id = serializers.IntegerField()

    # 指定所属分类信息 关联嵌套返回
    category = serializers.StringRelatedField(read_only=True)
    # 指定所属spu表信息 关联嵌套返回
    spu = serializers.StringRelatedField(read_only=True)
    # 指定所SKU关联的所有选项信息 关联嵌套返回
    specs = SKUSpecificationSerializer(many=True)

    class Meta:
        model = SKU
        fields = '__all__'

    def create(self, validated_data):
        """
        自定义create方法实现在创建SKU对象的时候，也创建对应的SKUSpecification表数据
        :param validated_data: 已通过反序列化的数据
        :return: SKU对象
        """

        # 默认在创建SKU对象的时候，不会创建对应的SKUSpecification表数据
        specs = validated_data.pop('specs')

        # 显式的开启一个事务
        with transaction.atomic():
            # 创建事务保存点
            save_id = transaction.savepoint()

            try:
                # instance表示新建的SKU对象
                instance = super().create(validated_data)

                for temp in specs:
                    temp['sku_id'] = instance.id
                    # temp = {'sku_id': xx, 'spec_id': xx, 'option_id': xx}
                    SKUSpecification.objects.create(**temp)
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
            transaction.savepoint_commit(save_id)

        return instance

    def update(self, instance, validated_data):

        specs = validated_data.pop('specs')

        with transaction.atomic():
            save_id = transaction.savepoint()

            try:
                # 更新SKUSpecification表数据
                # for temp in specs:
                #     # 获取SKUSpecification表对象
                #     sku_spec = SKUSpecification.objects.get(sku_id=instance.id, spec_id=temp['spec_id'])
                #     sku_spec.option_id = temp['option_id']
                #     sku_spec.save()

                SKUSpecification.objects.filter(sku_id=instance.id).delete()
                for temp in specs:
                    temp['sku_id'] = instance.id
                    SKUSpecification.objects.create(**temp)
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
            transaction.savepoint_commit(save_id)

        return super().update(instance, validated_data)


class GoodsCategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""

    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']


class SPUSimpleSerializer(serializers.ModelSerializer):
    """商品SPU表小型序列化器"""

    class Meta:
        model = SPU
        fields = ['id', 'name']


class SPUOptionSerializer(serializers.ModelSerializer):
    """SPU规格选项序列化器"""

    # SpecificationOption表中的外键spec_id关联了SPUSpecification表
    spec_id = serializers.IntegerField()
    spec = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SpecificationOption
        fields = ['id', 'value', 'spec_id', 'spec']


class SPUSpecificationSerializer(serializers.ModelSerializer):
    """SPU规格序列化器"""

    # SPUSpecification中的外键spu关联了SPU商品表
    spu_id = serializers.IntegerField()
    spu = serializers.StringRelatedField(read_only=True)

    # 使用规格选项序列化器进行关联序列化
    options = SPUOptionSerializer(read_only=True, many=True)

    class Meta:
        model = SPUSpecification
        fields = ['id', 'name', 'spu_id', 'spu', 'options']


class BrandSerializer(serializers.ModelSerializer):
    """商品品牌模型类序列化器"""

    class Meta:
        model = Brand
        fields = '__all__'

    def create(self, validated_data):
        """重写create方法，实现品牌的logo上传"""

        # 获取前端传递的logo文件对象
        # logo = open('上传的图片', 'rb')
        logo = validated_data.pop('logo')
        # 获取图片上传到FastDFS成功后的url

        logo_url = get_fdfs_url(logo)

        validated_data['logo'] = logo_url
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """重写update方法，实现品牌的logo更新"""

        logo = validated_data.pop('logo')
        logo_url = get_fdfs_url(logo)

        instance.logo = logo_url
        instance.save()
        return instance


class SPUSerializer(serializers.ModelSerializer):
    """SPU模型类序列化器"""

    # SPU模型类默认自动构建关联表id字段，但序列化时不会自动映射此字段
    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()

    # 指定所属品牌名称 关联嵌套返回
    brand = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SPU
        exclude = ['category1', 'category2', 'category3']


class GoodsChannelSerializer(serializers.ModelSerializer):
    """GoodsChannel模型类序列化器"""

    category_id = serializers.IntegerField()
    group_id = serializers.IntegerField()

    category = serializers.StringRelatedField(read_only=True)
    group = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsChannel
        fields = '__all__'


class GoodsChannelGroupSerializer(serializers.ModelSerializer):
    """GoodsChannelGroup模型类序列化器"""

    class Meta:
        model = GoodsChannelGroup
        fields = '__all__'


class SKUImageSerializer(serializers.ModelSerializer):
    """SKUImage模型类序列化器"""

    class Meta:
        model = SKUImage
        fields = '__all__'  # ImageField类型自动序列化为image.url

    def create(self, validated_data):
        """重写create方法，实现SKUImage表的image上传"""
        """
        validated_data = {'image': < InMemoryUploadedFile: weibo.png(image/png) >, 
                        'sku': < SKU: 20: HUAWEIP30 >}
        """

        # 获取前端传递的image文件对象
        # image = open('上传的图片', 'rb')
        image = validated_data.pop('image')
        sku = validated_data.pop('sku')

        # 获取图片上传到FastDFS成功后的url
        image_url = get_fdfs_url(image)
        if not sku.default_image:
            sku.default_image = image_url
            sku.save()
        validated_data['image'] = image_url
        validated_data['sku'] = sku

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """重写update方法，实现SKUImage表的image更新"""

        image = validated_data.pop('image')
        image_url = get_fdfs_url(image)

        instance.image = image_url
        instance.save()
        return instance


class SKUSimpleSerializer(serializers.ModelSerializer):
    """SKU模型类小型序列化器"""

    class Meta:
        model = SKU
        fields = ['id', 'name', 'default_image']
