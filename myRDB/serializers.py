from rest_framework import serializers
from .models import Orga, Department, Group, ZI_Organisation, TF_Application, TF, GF, AF, Role, User


class OrgaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orga
        fields = ('id', 'team', 'theme_owner')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'department_name')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'group_name')


class ZI_OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZI_Organisation
        fields = ('id', 'zi_organisation_name')


class TF_ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TF_Application
        fields = ('id', 'application_name')


class TFSerializer(serializers.ModelSerializer):
    class Meta:
        model = TF
        fields = ('id', 'tf_name', 'tf_description', 'tf_owner_orga', 'tf_application', 'criticality',
                  'highest_criticality_in_AF')


class GFSerializer(serializers.ModelSerializer):
    class Meta:
        model = GF
        fields = ('id', 'gf_name', 'gf_description', 'tfs')


class AFSerializer(serializers.ModelSerializer):
    class Meta:
        model = AF
        fields = ('id', 'af_name', 'af_description', 'af_applied', 'af_valid_from', 'af_valid_till', 'gfs')


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orga
        fields = ('id', 'role_name', 'role_description', 'afs')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orga
        fields = (
        'id', 'identity', 'name', 'first_name', 'deleted', 'orga_id', 'department_id', 'group_id', 'zi_organisation_id',
        'roles', 'direct_connect_afs', 'direct_connect_gfs', 'direct_connect_tfs', 'is_staff', 'password')
